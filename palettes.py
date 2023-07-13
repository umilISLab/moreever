from bokeh import palettes
from corpora import corpora

pal_list = [
    palettes.Oranges256,
    palettes.Greens256,
    palettes.Blues256,
    palettes.Greys256,
    palettes.Reds256,
    palettes.Purples256,
]

assert corpora == [
    "Italy",
    "Germany",
    "Portugal",
], "For 3-country fairy tale corpora, an exact match of colors is intended"

# This will be meaningful for other corpora
assert len(corpora) <= len(
    pal_list
), "Number of corpora greater than number of supported color palettes"

pal = {c: pal_list[i] for i, c in enumerate(corpora)}
