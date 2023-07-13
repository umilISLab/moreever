"""Functionality related to the manipulation of similarity objects"""
from typing import Dict, List
from glob import glob

import pandas as pd  # type: ignore

from bokeh.models import LinearColorMapper, LabelSet, ColumnDataSource  # type: ignore
from bokeh import palettes  # type: ignore
from bokeh.plotting import figure, show, output_file  # type: ignore

from algo import algos


def last_available_iteration(
    model_dir: str, tkn: str, algo: str, epochs: int = 200
) -> int:
    m = -1
    for f in glob(f"{model_dir}/M0.{tkn}.e{epochs}.{algo}.?"):
        n = int(f.split(".")[-1])
        if n > m:
            m = n
    return m


def calc_dist(
    _,
    keywords: List[str],
    variant: int,
    tkn: str,
    model_dir: str,
    algo: str = "ft",
    epochs: int = 200,
    iteration: int = 0,
):
    """
    variant is one of 0, 1, 2, 3
    returns list of lists that can be given as parameter to constructor of dataframe
    """
    model = algos[algo].load(
        f"{model_dir}/{variant}.{tkn}.e{epochs}.{algo}.{iteration}"
    )
    d: Dict[str, Dict[str, str]] = {}
    for i, k in enumerate(keywords):
        if k not in d:
            d[k] = {}
        # d[k][k] = f"{model.wv.similarity(k, k):.2f}"
        for x in keywords[i:]:
            try:
                d[k][x] = f"{model.wv.similarity(k, x):.2f}"
            except KeyError:
                d[k][x] = "0"
            if x not in d:
                d[x] = {}
            d[x][k] = d[k][x]
    return d


def calc_shift(
    _,
    keywords: List[str],
    variant: int,
    tkn: str,
    model_dir: str,
    algo: str = "ft",
    epochs: int = 200,
    iteration: int = 0,
):
    """
    variant is one of 0, 1, 2, 3
    returns list of lists that can be given as parameter to constructor of dataframe
    """
    m0 = algos[algo].load(f"{model_dir}/all.{tkn}.e{epochs}.{algo}.{iteration}")
    model = algos[algo].load(
        f"{model_dir}/{variant}.{tkn}.e{epochs}.{algo}.{iteration}"
    )
    d: Dict[str, Dict[str, str]] = {}
    for i, k in enumerate(keywords):
        if k not in d:
            d[k] = {}
        # d[k][k] = f"{model.wv.similarity(k, k):.2f}"
        for x in keywords[i:]:
            try:
                d[k][x] = f"{model.wv.similarity(k, x)-m0.wv.similarity(k, x):.2f}"
            except KeyError:
                d[k][x] = "0"
            if x not in d:
                d[x] = {}
            d[x][k] = d[k][x]
    return d


def calc_agg(
    agg,
    keywords: List[str],
    variant: int,
    tkn: str,
    model_dir: str,
    algo: str = "ft",
    epochs: int = 200,
):
    """
    :param func agg: a function that takes a list
    variant is one of 0, 1, 2, 3
    returns list of lists that can be given as parameter to constructor of dataframe
    """
    models = [
        algos[algo].load(f"{model_dir}/all.{tkn}.e{epochs}.{algo}.{iteration}")
        for iteration in range(
            0, last_available_iteration(model_dir, tkn, algo, epochs)
        )
    ]
    d: Dict[str, Dict[str, str]] = {}
    for i, k in enumerate(keywords):
        if k not in d:
            d[k] = {}
        # d[k][k] = f"{model.wv.similarity(k, k):.2f}"
        for x in keywords[i:]:
            try:
                m = agg([m.wv.similarity(k, x) for m in models])
                d[k][x] = f"{m:0.3f}"
            except KeyError:
                d[k][x] = "0"
            if x not in d:
                d[x] = {}
            d[x][k] = d[k][x]
    return d


def render(title: str, df: pd.DataFrame, fname: str = "distance.html"):
    """Renders a similarity matrix from a dataframe with columns (from, to, dist)"""
    output_file(
        # filename=f"site/{tkn}/distance.html",
        filename=fname,
        title=title,
    )
    keywords = list(df.loc[:, "from"].unique())
    source = ColumnDataSource(data=df)

    p = figure(
        title=title,
        y_range=keywords,
        x_range=keywords,
        x_axis_location="above",
        width=30 * len(keywords),
        height=30 * len(keywords),
        tools="hover",
        tooltips=[("", "@from/@to")],
    )

    mapper = LinearColorMapper(
        palette=palettes.Greens256,
        low=df["dist"].apply(pd.to_numeric).max(),
        high=df["dist"].apply(pd.to_numeric).min(),
    )
    p.rect(
        x="from",
        y="to",
        width=1,
        height=1,
        source=source,
        fill_color={"field": "dist", "transform": mapper},
        line_color=None,
    )

    labels = LabelSet(
        x="from",
        y="to",
        text="dist",
        y_offset=-5,
        text_align="center",
        level="glyph",
        text_color="grey",
        text_font_size="0.8em",
        source=source,
    )
    p.add_layout(labels)

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    # p.axis.major_label_text_font_size = "7px"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = "#eee"
    p.ygrid.grid_line_color = "#eee"

    show(p)
