#!/bin/python
"""Generate a heatmap of texts/stories vs labels"""
from typing import Dict, List, Tuple

import pandas as pd  # type: ignore

from settings import CLEAN_THRESHOLD, VOCAB

from corpora import corpora, country2code
from stemmers import stemmers
from palettes import pal_seq

from util import fname2name, fname2path
from persistence import tokenize_values, load_source, calc_occurences

from bokeh.models import LinearColorMapper, LabelSet, ColumnDataSource, TapTool, OpenURL  # type: ignore
from bokeh.plotting import figure  # type: ignore
from bokeh.resources import CDN  # type: ignore
from bokeh.embed import file_html  # type: ignore


def render(tkn: str, flat: bool = False, aggregated=False) -> str:
    """Needs either vocab/fname or rest of named parameters.

    Args:
        tkn (str): stemmer name, see semmers
        flat (bool): aggregate tokens by values
        aggregated (bool): aggregate texts by corpora
    """
    occurences, _, occurences_backref = calc_occurences(tkn, flat, aggregated)

    interactive = "" if aggregated else "Clickable "
    xaxis = "Labels" if flat else "Values"
    yaxis = "Corpora" if aggregated else "Texts"
    title = f"{interactive}Map of {xaxis} in {yaxis} (tokenisation: {tkn})"
    # output_file(filename=f"site/{tkn}/{vocab}/map.html", title=title)

    # print(occurences)

    data = [
        [
            k[0].split("/")[0],
            fname2name(k[0])
            + ("" if aggregated else f" [{country2code[k[0].split('/')[0]]}]"),
            k[1],
            v,
            str(v),
            # f"/index.html#/{tkn}/{vocab.replace('.flat', '')}/{k[0]}.html",
            f"/index.html#/{tkn}/{VOCAB}/{fname2path(k[0])}",
        ]
        for k, v in occurences.items()
        if v >= CLEAN_THRESHOLD
    ]
    df = pd.DataFrame(data)
    df.columns = ["country", "text", "value", "count", "label", "url"]  # type: ignore
    value_range = sorted(
        list(occurences_backref.keys()),
        key=lambda x: -sum(occurences_backref[x].values()),
    )

    text_range = (
        sorted(set(df["text"]))[::-1]
        if aggregated
        else list(df.groupby(["text"])["count"].sum().sort_values().index)
    )
    # text_range =  list(df.groupby(["text"])["count"].sum().sort_values().index)
    max_count = df["count"].max()

    source = ColumnDataSource(data=df)

    p = figure(
        title=title,
        y_range=text_range,
        x_range=value_range,
        x_axis_location="above",
        width=15 * len(value_range) + 450,
        height=15 * len(text_range) + 150,
        # toolbar_location = None,
        tools="" if aggregated else "tap",
        tooltips=[("label", "@value/@text: @count")],
    )

    for c in corpora:
        gmapper = LinearColorMapper(palette=pal_seq[c], low=max_count, high=0)
        gsource = ColumnDataSource(data=df[df["country"] == c])
        p.rect(
            x="value",
            y="text",
            width=1,
            height=1,
            source=gsource,
            fill_color={"field": "count", "transform": gmapper},
            line_color=None,
        )

    labels = LabelSet(
        x="value",
        y="text",
        text="label",
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
    p.xaxis.major_label_orientation = 1  # .4
    p.xgrid.grid_line_color = "#eee"
    p.ygrid.grid_line_color = "#eee"
    # p.toolbar.logo = None
    # p.toolbar_location = None

    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url="@url")

    return file_html(p, CDN, title)


if __name__ == "__main__":
    fname = "values-edited.flat"
    # fname = "values-flat"
    tkn = "sb"
    render(tkn, fname)
