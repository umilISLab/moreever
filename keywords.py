from typing import Dict, List, Set

import itertools

from create import tokenize_values, load_source, calc_occurences

from stemmers import stemmers
from corpora import corpora
from template import venn_templ


def render(tkn: str, fname: str):
    values, _ = tokenize_values(tkn, fname=fname)
    _, tokenized = load_source(stemmers[tkn], corpora)
    _, occurences_tv, _ = calc_occurences(values, tokenized)

    ckeywords: Dict[str, Set[str]] = {}
    for c in corpora:
        ckeywords[c] = set(
            itertools.chain(
                *[list(v.keys()) for k, v in occurences_tv.items() if k.startswith(c)]
            )
        )

    de_keywords = ckeywords["Germany"]
    it_keywords = ckeywords["Italy"]
    pt_keywords = ckeywords["Portugal"]

    params = {
        "de_it_pt": de_keywords & it_keywords & pt_keywords,
        "de": de_keywords - it_keywords - pt_keywords,
        "it": it_keywords - de_keywords - pt_keywords,
        "pt": pt_keywords - de_keywords - it_keywords,
    }
    params["de_it"] = (de_keywords & it_keywords) - params["de_it_pt"]
    params["de_pt"] = (de_keywords & pt_keywords) - params["de_it_pt"]
    params["it_pt"] = (it_keywords & pt_keywords) - params["de_it_pt"]

    params2 = {
        k: "".join(
            [
                f'<tspan x="0" y="{i*10}">{p}</tspan>'
                for i, p in enumerate(list(params[k]))
            ]
        )
        for k, v in params.items()
    }

    result = venn_templ.format(**params2)
    with open(f"site/{tkn}/keywords.svg", "w") as f:
        f.writelines(result)
