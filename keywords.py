from typing import Dict, List, Set

import itertools

from create import tokenize_values, load_source, calc_occurences

from stemmers import stemmers
from corpora import corpora
from template import venn_templ


def render(
    tkn: str,
    fname: str = "",
    values: Dict[str, List[str]] = {},
    tokenized: Dict[str, Dict[str, List[List[str]]]] = {},
    occurences_tv: Dict[str, Dict[str, int]] = {},
):
    """_summary_

    Args:
        tkn (str): stemmer name, see semmers
        fname (str, optional): need to provide either fname or other parameters.
        values (Dict[str, List[str]], optional): see create.tokenize_values(). Recalculated when missing.
        tokenized (Dict[str, Dict[str, List[List[str]]]], optional): see create.load_source(). Recalculated when missing.
        occurences_tv (Dict[str, Dict[str, int]], optional): see create.calc_occurences(). Recalculated when missing.
    """
    if not values or not tokenized or not occurences_tv:
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
