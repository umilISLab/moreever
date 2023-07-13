#!/bin/python
"""Generate a heatmap of texts/stories vs labels"""

from glob import glob

import pandas as pd  # type: ignore

from corpora import corpora as corpora, country2code
from util import story_tokenize, collect_tokens, fname2name, stats
from create import tokenize_values, load_source, calc_occurences
from palettes import pal

from bokeh.models import LinearColorMapper, LabelSet, ColumnDataSource, TapTool, OpenURL  # type: ignore
from bokeh.plotting import figure, save, output_file  # type: ignore


from stemmers import stemmers


def render(tkn: str, fname: str):
    title = f"Clickable Map of Values in Fairy Tales (tokenisation: {tkn})"
    output_file(filename=f"site/{tkn}/map.html", title=title)

    values, _ = tokenize_values(tkn, fname=fname)
    _, tokenized = load_source(stemmers[tkn], corpora)
    occurences, _, occurences_backref = calc_occurences(values, tokenized)

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
        width=17 * len(value_range),
        height=1100,
        # toolbar_location = None,
        tools="tap",
        tooltips=[("label", "@value/@text: @count")],
    )

    for c in corpora:
        gmapper = LinearColorMapper(palette=pal[c], low=max_count, high=0)
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

    save(p)


if __name__ == "__main__":
    fname = "values-edited.flat"
    # fname = "values-flat"
    tkn = "sb"
    render(tkn, fname)
