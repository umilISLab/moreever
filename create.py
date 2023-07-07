from typing import Dict, List, Tuple

from glob import glob

# import pandas as pd
# import numpy as np
# from tqdm.notebook import tqdm

from stemmers import stemmers
from util import story_tokenize, collect_tokens


def tokenize_values(
    func_name: str = "sb", fname="values-edited"
) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """fname without extension"""
    token_func = stemmers[func_name]
    values: Dict[str, List[str]] = {}
    valuesbackref: Dict[str, str] = {}
    with open(f"{fname}.txt") as f:
        flines = f.readlines()
        for l in flines:
            if not l.strip():
                continue
            fitems = [x.strip().lower() for x in l.split(",") if x.strip()]
            stemmed_fitems = [token_func(x) for x in fitems]
            values[stemmed_fitems[0]] = stemmed_fitems
            for i in stemmed_fitems:
                # if i in valuesbackref:
                #     print(i, stemmed_fitems[0])
                valuesbackref[i] = stemmed_fitems[0]
    with open(f"site/{func_name}/{fname}.txt", "w") as fout:
        fout.writelines("\n".join(", ".join(v) for v in values.values()))
    return values, valuesbackref


def load_source(
    token_func, document_folders: List[str]  # , annotate: bool = False
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]:
    fulltexts: Dict[str, Dict[str, str]] = {}
    tokenized: Dict[str, Dict[str, List[List[str]]]] = {}
    for country in document_folders:
        c = country[0]
        fulltexts[c] = {}
        tokenized[c] = {}
        for fname in glob(f"./stories/{country}/*.txt"):
            with open(fname) as f:
                talename = fname.split("/")[-1].split(".")[-2]
                fulltexts[c][talename] = "".join(f.readlines())
                tokenized[c][talename] = story_tokenize(
                    token_func, fulltexts[c][talename]
                )
    return fulltexts, tokenized


def calc_occurences(
    values: Dict[str, List[str]], tokenized: Dict[str, Dict[str, List[str]]]
) -> Tuple[
    Dict[Tuple[str, str], int], Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]
]:
    occurences: Dict[Tuple[str, str], int] = {}  # (text_name, value): count)
    occurences_tv: Dict[str, Dict[str, int]] = {}  # text_name: (value: count)
    occurences_backref: Dict[str, Dict[str, int]] = {}  # value: (text_name:count)
    for country, chapters in tokenized.items():
        for chapter, text in chapters.items():
            text_name = f"{country[0]}/{chapter}"
            for value_name, synonyms in values.items():
                cnt = sum(
                    sum(phrase.count(keyword) for keyword in synonyms)
                    for phrase in text
                )
                if not cnt:
                    continue

                occurences[(text_name, value_name)] = cnt

                if text_name not in occurences_tv:
                    occurences_tv[text_name] = {}
                assert value_name not in occurences_tv[text_name]
                occurences_tv[text_name][value_name] = cnt

                if value_name not in occurences_backref:
                    occurences_backref[value_name] = {}
                assert text_name not in occurences_backref[value_name]
                occurences_backref[value_name][text_name] = cnt

    return occurences, occurences_tv, occurences_backref


def annotate_occurences(
    tokenized: Dict[str, Dict[str, List[List[str]]]], values_br: Dict[str, str]
):
    """
    Emphasises relationships between keywords and labels/values,
    by inserting a bracketed label before and after every keyword

    >>> tokenized = {'a':{'a':[['aa', 'bb', 'cc']]}}
    >>> values = {'bb': 'dd'}
    >>> annotate_occurences(tokenized, values)
    {'a': {'a': [['aa', 'dd', 'bb', 'dd', 'cc']]}}
    """
    for country, tales in tokenized.items():
        for tale, tokens in tales.items():
            overall = []
            for sentence in tokens:
                updated = []
                for token in sentence:
                    if token in values_br.keys():
                        updated += [values_br[token], token, values_br[token]]
                    else:
                        updated += [token]
                overall += [updated]
            tokenized[country][tale] = overall
    return tokenized


if __name__ == "__main__":
    print(tokenize_values(fname="values-flat"))
