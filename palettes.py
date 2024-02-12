from bokeh import palettes
from corpora import corpora

pos_range = range(2, 256, 2)
neg_range = list(pos_range).copy()
neg_range.reverse()

# TODO: Could be expanded with CMYK colors,
# notice that the provided ColorBrewer palettes are not exactly the basic RGB colors
pal_seq_list = [
    palettes.Greys256,  # first color matches complete corpus (union of all corpora)
    palettes.Oranges256,
    palettes.Greens256,
    palettes.Blues256,
    palettes.Reds256,
    palettes.Purples256,
]

# Negative for grey is red, and is grey for other colors
pal_div_list = [
    tuple(
        [palettes.Reds256[n] for n in pos_range]
        + ["#ffffff"]
        + [palettes.Greys256[n] for n in neg_range]
    )
]
for i in range(1, len(pal_seq_list)):
    pal_div_list += [
        tuple(
            [palettes.Greys256[n] for n in pos_range]
            + ["#ffffff"]
            + [pal_seq_list[i][n] for n in neg_range]
        )
    ]

# assert corpora == [
#     "Italy",
#     "Germany",
#     "Portugal",
# ], "For 3-country fairy tale corpora, an exact match of colors is intended"

# This will be meaningful for other corpora
assert len(corpora) + 1 <= len(
    pal_seq_list
), "Number of corpora is greater than 5 (number of supported color palettes)"

pal_seq = dict(zip(["all"] + corpora, pal_seq_list))
pal_div = dict(zip(["all"] + corpora, pal_div_list))
# pal_seq = {c: pal_seq_list[i] for i, c in enumerate(["all"] + corpora)}
# pal_div = {c: pal_seq_list[i] for i, c in enumerate(["all"] + corpora)}
