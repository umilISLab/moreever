from typing import Dict

import os
import csv
from glob import glob

import colorcet as cc  # type: ignore

from settings import VOCAB

from corpora import corpora
from stemmers import stemmers, stemmer_labels
from template import title_templ, span_templ, select_option_templ
from template import index_templ, corpus_templ, text_templ, list_templ, values_templ
from template import value_link_templ, list_link_templ


from util import fname2name
from datamodel import Annotator

from create import tokenize_values, load_source, calc_occurences


def values_css(stemmer: str, vocab: str) -> str:
    mapping: Dict[str, str] = {}
    with open(f"site/{stemmer}/{vocab}.csv") as f:
        for i, l in enumerate(csv.reader(f)):
            mapping[l[0]] = cc.glasbey_cool[i]
    # print(f"Styles for {stemmer}: {mapping}")
    return "\n".join(f".{k} {{background-color: {v}}}" for k, v in mapping.items())


def text_anchor_dict(stemmer: str, vocab: str, corpus: str) -> Dict[str, str]:
    names = {}
    # for fname in glob(f"site/{stemmer}/{vocab}/{corpus}/*.html"):
    # print(corpus)
    for raw_fname in glob(f"corpora/{corpus}/*.txt"):
        # print(raw_fname)
        fname = raw_fname.replace("corpora", f"site/{stemmer}/{vocab}")
        fname = fname.replace(f"{corpus}/", f"{corpus}.html#")
        fname = fname.replace(".txt", "")
        # print(fname)
        names[fname2name(fname)] = fname.lower()
    return names


def index_html() -> str:
    stemmer_default = next(reversed(stemmers.keys()))
    stemmers_html = "".join(
        select_option_templ.format(value=k, label=stemmer_labels[k], default="selected" if k==stemmer_default else "") for k in stemmers
    )

    corpora_html = select_option_templ.format(value="all", label="all", default="")
    corpora_html += "".join(
        select_option_templ.format(value=c, label=c, default="") for c in corpora
    )
    corpus_default = next(iter(corpora))

    tokenize_values(stemmer_default, VOCAB)
    return index_templ.format(
        stemmers=stemmers_html,
        corpora=corpora_html,
        vocab=VOCAB,
        stem=stemmer_default,
        corpus=corpus_default,
    )


def page_corpus_html(
    corpus: str, stemmer: str, vocab: str, values_br: Dict[str, str] = {}
) -> str:
    """generates a unified page for stories in a corpus

    Args:
        corpus (str): one of the corpora
        stemmer (str): one of the stemmers
        values_br (Dict[str, str], optional): _description_. Defaults to {}.

    Returns:
        str: the annotated HTML page
    """
    annotated = ""

    fulltext = ""
    for fname in sorted(glob(f"corpora/{corpus}/*.txt")):
        with open(fname) as fin:
            ftitle = fname2name(fname)
            # parts = fname.split("_")[1:]
            fid = "_".join(ftitle.split(" ")).lower()
            # ftitle = " ".join(parts)
            fulltext += "<br/>" + title_templ.format(id=fid, level=2, content=ftitle) + fin.read() + "<br/>"
    a = Annotator(stemmer, fulltext, values_br)
    annotated = a.rich_text()
    return corpus_templ.format(title=corpus, body=annotated)


def text_anchor_html(stemmer: str, vocab: str, corpus: str = "", from_parent=False) -> str:
    """Refers to texts in a united corpus file.
    :param str corpus: Specifies corpus/country. If not set, will do for all
    :param bool from_parent: Specifies whether the generated file will be in the parent directory,
        so that URLs are adapted accordingly. This is not intended to be set manually
    """
    if not corpus:
        return "\n".join(text_anchor_html(stemmer, vocab, c, True) for c in corpora)
    names = text_anchor_dict(stemmer, vocab, corpus)
    result = []
    for name in sorted(names.keys()):
        fname = names[name]
        # print(fname)
        url = (
            fname.replace(f"site/{stemmer}/{vocab}/", "")
            if from_parent
            else fname.replace(f"site/{stemmer}/{vocab}/", "../")
        )
        # print(url)
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
    all_texts = text_dict(stemmer, vocab, corpus)
    # print(stemmer, corpus, all_texts)
    names = {}
    for name, fname in all_texts.items():
        # sample fname is 'site/sb/Germany/65_Allerleirauh.html'
        # sample shortname is 'Germany/65_Allerleirauh'
        shortname = fname[len(f"site/{stemmer}/{vocab}/") : -5]
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

    values, _ = tokenize_values(stemmer, f"{vocab}.flat")
    _, tokenized = load_source(stemmers[stemmer], corpora)
    _, _, occurences_backref = calc_occurences(values, tokenized)

    with open(f"{vocab}.csv") as fin:
        for line in csv.reader(fin):
            if not line:
                continue
            stems = [stemmers[stemmer](v.strip().lower()) for v in line]
            links = []
            for i, s in enumerate(stems):
                # print(occurences_backref.keys())
                found = s in occurences_backref and len(occurences_backref[s]) > 0
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
    return values_templ.format(title="Vocabulary", body=body)
