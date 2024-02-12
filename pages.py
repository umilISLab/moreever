from typing import Dict

import os
import csv
from glob import glob

import colorcet as cc  # type: ignore

from corpora import corpora
from stemmers import stemmers
from template import (
    tale_templ,
    list_templ,
    values_templ,
    value_link_templ,
    list_link_templ,
    span_templ,
)

from util import fname2name
from datamodel import Annotator


def values_css(stemmer: str, vocab: str) -> str:
    mapping: Dict[str, str] = {}
    with open(f"site/{stemmer}/{vocab}.csv") as f:
        for i, l in enumerate(csv.reader(f)):
            mapping[l[0]] = cc.glasbey_cool[i]
    # print(f"Styles for {stemmer}: {mapping}")
    return "\n".join(f".{k} {{background-color: {v}}}" for k, v in mapping.items())


def tale_dict(stemmer: str, vocab: str, corpus: str) -> Dict[str, str]:
    names = {}
    # for fname in glob(f"site/{stemmer}/{vocab}/{corpus}/*.html"):
    # print(corpus)
    print(corpus)
    for raw_fname in glob(f"corpora/{corpus}/*.txt"):
        # print(raw_fname)
        fname = raw_fname.replace("corpora", f"site/{stemmer}/{vocab}").replace(".txt", ".html")
        print(fname)
        names[fname2name(fname)] = fname
    return names


def page_html(fname: str, stemmer: str, vocab: str, values_br: Dict[str, str] = {}) -> str:
    """generates the story page

    Args:
        fname (str): one of "corpora/{corpus}/*.txt"
        stemmer (str): one of the stemmers
        values_br (Dict[str, str], optional): _description_. Defaults to {}.

    Returns:
        str: the annotated HTML page
    """
    fname_path = fname.split(".")[0]
    fname_base = fname_path.split("/")[-1]
    text = " ".join(fname_base.split("_")[1:])
    annotated = ""

    with open(fname) as fin:
        fulltext = fin.read()
    a = Annotator(stemmer, fulltext, values_br)
    annotated = a.rich_text()
    return tale_templ.format(title=text, body=annotated)


def tale_html(stemmer: str, vocab: str, corpus: str = "", from_parent=False) -> str:
    """
    :param str corpus: Specifies corpus/country. If not set, will do for all
    :param bool from_parent: Specifies whether the generated file will be in the parent directory,
        so that URLs are adapted accordingly. This is not intended to be set manually
    """
    if not corpus:
        return "\n".join(tale_html(stemmer, vocab, c, True) for c in corpora)
    names = tale_dict(stemmer, vocab, corpus)
    result = []
    for name in sorted(names.keys()):
        fname = names[name]
        url = (
            fname.replace(f"site/{stemmer}/{vocab}/", "")
            if from_parent
            else fname.replace(f"site/{stemmer}/{vocab}/{corpus}/", "")
        )
        result += [f"<div><a href='{url}' target='fulltext'>{name}</a></div>"]
    return "\n".join(result)


def value_list_html(
    occurences_backref: Dict[str, Dict[str, int]],
    vocab: str,
    stemmer: str,
    label: str,
    corpus: str = "",
    from_parent=False,
):
    if not corpus:
        return "\n".join(
            value_list_html(occurences_backref, vocab, stemmer, label, c, True)
            for c in corpora
        )
    all_tales = tale_dict(stemmer, vocab, corpus)
    # print(stemmer, country, all_tales)
    names = {}
    for name, fname in all_tales.items():
        # sample fname is 'site/sb/Germany/65_Allerleirauh.html'
        # sample shortname is 'Germany/65_Allerleirauh'
        shortname = fname[6 + len(stemmer) : -5]
        if shortname in occurences_backref[label]:
            names[f"{name} ({occurences_backref[label][shortname]})"] = fname
    result = []
    for name in sorted(names.keys()):
        fname = names[name]
        url = fname.replace(f"site/{stemmer}/{vocab}/", f"../" if from_parent else "")
        result += [f"<div><a href='{url}' target='fulltext'>{name}</a></div>"]
    return "\n".join(result)


def values_html(stemmer: str, vocab: str) -> str:
    """The page that list all the values, see values_templ for reference"""
    title = "Values and Labels"
    result = []
    with open(f"{vocab}.csv") as fin:
        for line in csv.reader(fin):
            if not line:
                continue
            stems = [stemmers[stemmer](v.strip().lower()) for v in line]
            links = []
            for i, s in enumerate(stems):
                found = os.path.exists(f"site/{stemmer}/{vocab}/values/{s}.html")
                title = s if found else f"{s} (not found)"
                styled = (
                    span_templ.format(
                        id=s + "-tag",
                        type=f"{stemmer} {s}" if i == 0 else stemmer,
                        title=title,
                        content=s,
                    )
                    # TODO: Understand why first letter of ending is different for values and labels
                    + line[i][len(s) + (1 if i else 0) :]
                )
                linked = (
                    list_link_templ.format(
                        id=s + "-link",
                        url=f"/{stemmer}/{vocab}/values/{s}.html",
                        type=f"{stemmer}",
                        title=title,
                        content=styled,
                    )
                    if found
                    else styled
                )
                links += [linked]
            result += [", ".join(links)]
    # body = "<p>" + "</p><p>".join(result) + "</p>"
    body = "<br/>".join(result)
    return values_templ.format(title="Values", body=body)
