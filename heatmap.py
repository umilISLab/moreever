#!/bin/python
"""Generate a heatmap of texts/stories vs labels"""
from typing import Dict, List, Tuple

import pandas as pd  # type: ignore

from corpora import corpora, country2code
from stemmers import stemmers
from palettes import pal_seq

from util import fname2name
from create import tokenize_values, load_source, calc_occurences

from bokeh.models import LinearColorMapper, LabelSet, ColumnDataSource, TapTool, OpenURL  # type: ignore
from bokeh.plotting import figure  # type: ignore
from bokeh.resources import CDN  # type: ignore
from bokeh.embed import file_html  # type: ignore


def render(
    tkn: str,
    vocab: str = "",
    values: Dict[str, List[str]] = {},
    tokenized: Dict[str, Dict[str, List[List[str]]]] = {},
    occurences: Dict[Tuple[str, str], int] = {},
    occurences_backref: Dict[str, Dict[str, int]] = {},
) -> str:
    """Needs either vocab/fname or rest of named parameters.

    Args:
        tkn (str): stemmer name, see semmers
        fname (str, optional): need to provide either fname or other parameters
        values (Dict[str, List[str]], optional): see create.tokenize_values(). Recalculated when missing.
        tokenized (Dict[str, Dict[str, List[List[str]]]], optional): see create.load_source(). Recalculated when missing.
        occurences (Dict[Tuple[str, str], int], optional): see create.calc_occurences(). Recalculated when missing.
        occurences_backref (Dict[str, Dict[str, int]], optional): see create.calc_occurences(). Recalculated when missing.
    """
    if not values or not tokenized or not occurences or not occurences_backref:
        values, _ = tokenize_values(tkn, vocab)
        _, tokenized = load_source(stemmers[tkn], corpora)
        occurences, _, occurences_backref = calc_occurences(values, tokenized)

    title = f"Clickable Map of Values in Texts (tokenisation: {tkn})"
    # output_file(filename=f"site/{tkn}/{vocab}/map.html", title=title)

    data = [
        [
            k[0].split("/")[0],
            f"{fname2name(k[0])} [{country2code[k[0].split('/')[0]]}]",
            k[1],
            v,
            str(v),
            f"/index.html#/{tkn}/{k[0]}.html",
        ]
        for k, v in occurences.items()
    ]
    df = pd.DataFrame(data)
    df.columns = ["country", "text", "value", "count", "label", "url"]
    value_range = sorted(
        list(occurences_backref.keys()),
        key=lambda x: -sum(occurences_backref[x].values()),
    )

    text_range = list(df.groupby(["text"])["count"].sum().sort_values().index)
    max_count = df["count"].max()

    source = ColumnDataSource(data=df)

    p = figure(
        title=title,
        y_range=text_range,
        x_range=value_range,
        x_axis_location="above",
        width=15 * len(value_range) + 250,
        height=15 * len(text_range) + 150,
        # toolbar_location = None,
        tools="tap",
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
