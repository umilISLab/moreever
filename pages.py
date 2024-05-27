from typing import Dict

import os
import csv
from glob import glob

import colorcet as cc  # type: ignore
from urllib.parse import quote_plus

from settings import VOCAB, CORPORA, CLEAN_THRESHOLD

from corpora import corpora
from stemmers import stemmers, stemmer_labels
from template import title_templ, span_templ, select_option_templ, table_templ
from template import index_templ, corpus_templ, text_templ, list_templ, values_templ
from template import value_link_templ, list_link_templ

from util import fname2name, fname2path, path2corpus, path2name
from datamodel import Annotator
from hyper import enrich_value

# from create import tokenize_values, load_source, calc_occurences
from persistence import tokenize_values, load_source, calc_occurences
from persistence import corpora_stats, stemmers_values


def values_css(stemmer: str, vocab: str) -> str:
    mapping: Dict[str, str] = {}
    with open(f"vocab/{stemmer}/{vocab}.csv") as f:
        for i, l in enumerate(csv.reader(f)):
            mapping[l[0]] = cc.glasbey_cool[i]
    # print(f"Styles for {stemmer}: {mapping}")
    return "\n".join(f".{k} {{background-color: {v}}}" for k, v in mapping.items())


def text_anchor_dict(stemmer: str, vocab: str, corpus: str) -> Dict[str, str]:
    names = {}
    # for fname in glob(f"site/{stemmer}/{vocab}/{corpus}/*.html"):
    for fname in glob(f"corpora.{CORPORA}/{corpus}/*.txt"):
        names[fname2name(fname)] = f"site/{stemmer}/{vocab}/{fname2path(fname)}"
    return names


def index_html() -> str:
    stemmer_default = next(reversed(stemmers.keys()))
    stemmers_html = "".join(
        select_option_templ.format(
            value=k,
            label=stemmer_labels[k],
            default="selected" if k == stemmer_default else "",
        )
        for k in stemmers
    )

    corpora_html = select_option_templ.format(value="all", label="all", default="")
    corpora_html += "".join(
        select_option_templ.format(value=c, label=c, default="") for c in corpora
    )
    corpus_default = next(iter(corpora))

    text_default = "onboarding.html"

    tokenize_values(stemmer_default)
    return index_templ.format(
        stemmers=stemmers_html,
        corpora=corpora_html,
        vocab=VOCAB,
        stem=stemmer_default,
        corpus=corpus_default,
        text=text_default,
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
    for fname in sorted(glob(f"corpora.{CORPORA}/{corpus}/*.txt")):
        with open(fname) as fin:
            ftitle = fname2name(fname)
            # parts = fname.split("_")[1:]
            fid = "_".join(ftitle.split(" ")).lower()
            # ftitle = " ".join(parts)
            fulltext += (
                "<br/>"
                + title_templ.format(id=fid, level=2, content=ftitle)
                + fin.read()
                + "<br/>"
            )
    a = Annotator(stemmer, fulltext, values_br)
    annotated = a.rich_text()
    return corpus_templ.format(title=corpus, body=annotated)


def text_anchor_html(
    stemmer: str, vocab: str, corpus: str = "", from_parent=False
) -> str:
    """References to texts in united files per corpus.
    :param str corpus: Specifies corpus/country. If not set, will do for all
    :param bool from_parent: Specifies whether the generated file will be in the parent directory,
        so that URLs are adapted accordingly. This is not intended to be set manually
    """
    if not corpus:
        return "\n".join(text_anchor_html(stemmer, vocab, c, True) for c in corpora)
    names = text_anchor_dict(stemmer, vocab, corpus)
    # print(names)
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
    all_texts = text_anchor_dict(stemmer, vocab, corpus)
    # print(stemmer, corpus, all_texts)
    names = {}
    for name, fname in all_texts.items():
        # sample fname is 'site/sb/Germany/65_Allerleirauh.html'
        # sample shortname is 'Germany/65_Allerleirauh'
        # shortname = fname[len(f"site/{stemmer}/{vocab}/") : -5]
        shortname = f"{path2corpus(fname)}/{path2name(fname)}"
        # print(occurences_backref.keys())
        if shortname in occurences_backref[label]:
            names[f"{name} ({occurences_backref[label][shortname]})"] = fname
    result = []
    for name in sorted(names.keys()):
        fname = names[name]
        url = fname.replace(f"site/{stemmer}/{vocab}/", f"../" if from_parent else "")
        result += [f"<div><a href='{url}' target='fulltext'>{name}</a></div>"]
    return "\n".join(result)


def values_html(stemmer: str, vocab: str) -> str:
    """The page that list all the values, see values_templ for reference
    Args:
        stemmer - name as in stemmer.py
        vocab - list without path and extension
    """
    result = []

    _, _, occurences_backref = calc_occurences(stemmer, True)

    with open(f"vocab/{vocab}.csv") as fin:
        for line in csv.reader(fin):
            if not line:
                continue
            stems = [stemmers[stemmer](v.strip(), None) for v in line]
            links = {}
            # TODO: refactor: currently first handled separately in enrich_values, then merged and separated here
            first = None
            for i, s in enumerate(stems):
                found = len(occurences_backref[s]) if s in occurences_backref else 0
                linked = enrich_value(stemmer, vocab, line[i].strip(), s, found)
                if not i:
                    first = linked
                elif CLEAN_THRESHOLD <= found:
                    links[linked] = found
            tail = (
                list(links.keys())
                if CLEAN_THRESHOLD == 0
                else [k for k, v in sorted(links.items(), key=lambda item: -item[1])]
            )
            result += [", ".join([first] + tail)]
    body = '<div class="show"><p>' + "</p><p>".join(result) + "</p></div>"
    return values_templ.format(
        title="Vocabulary", body=body, vocab=vocab, stemmer=stemmer, button="Modify"
    )


def stats_html():
    body = []

    # corpora stats
    heading = (
        "<tr><th>"
        + "</th><th>".join(
            [
                "corpus",
                "texts",
                "sentences",
                "tokens",
                "avg.tokens",
                "labels",
                "avg.labels",
            ]
        )
        + "</th></tr>"
    )
    ctc = corpora_stats()
    data = [
        (
            corpus,
            str(count[0]),
            str(count[1]),
            f"{count[2]}",
            f"{count[2]/count[0]:.2f}",
            f"{count[3]}",
            f"{count[3]/count[0]:.2f}",
        )
        for corpus, count in ctc.items()
    ]
    txt, sent, tok, lbl = (sum(count) for count in zip(*ctc.values()))
    rows = [
        "<tr><td>" + '</td><td class="number">'.join(d) + "</td></tr>" for d in data
    ]
    totals = (
        "<tr><th>"
        + "</th><th class='number'>".join(
            [
                "totals",
                str(txt),
                str(sent),
                f"{tok}",
                f"{tok/txt:.3f}",
                f"{lbl}",
                f"{lbl/txt:.3f}",
            ]
        )
        + "</th></tr>"
    )
    corpora_stats_table = (
        '<table style="margin: 0 auto;">'
        + heading
        + "".join(rows)
        + totals
        + "</table>"
    )
    body += [corpora_stats_table]

    body += ["<br/><br/>"]

    # values x stemmers table
    data = stemmers_values()
    cols = list(stemmers)
    heading = (
        "<tr><th></th><th>"
        + "</th><th>".join([stemmer_labels[s].replace(" ", "<br/>") for s in cols])
        + "</th></tr>"
    )
    rows = []
    sums = [0] * len(cols)
    for d in data.keys():
        part = '</td><td class="number">'.join(
            [str(data[d][c] if d in data and c in data[d] else 0) for c in cols]
        )
        rows += [f"<tr><th>{d}</th><td class='number'>{part}</td></tr>"]
        for i, c in enumerate(cols):
            sums[i] += data[d][c] if d in data and c in data[d] else 0
    totals = (
        "<tr><th>totals</th><th>"
        + "</th><th class='number'>".join(str(s) for s in sums)
        + "</th></tr>"
    )
    stemmers_vocab_table = (
        '<table style="margin: 0 auto;">'
        + heading
        + "".join(rows)
        + totals
        + "</table>"
    )
    body += [stemmers_vocab_table]

    return table_templ.format(body="<br/>".join(body), title="")


def edit_vocab_html(stemmer: str, vocab: str) -> str:
    """same as values_html(), but editable"""
    with open(f"vocab/{vocab}.csv") as f:
        contents = "".join(f.readlines())
    body = f"""<textarea name="contents" id="contents">{contents}</textarea>"""
    return values_templ.format(
        title="Modify Vocabulary",
        body=body,
        vocab=vocab,
        stemmer=stemmer,
        button="Save",
    )


if __name__ == "__main__":
    # print(text_anchor_dict("lan", "Refined_dictionary.lan", "split"))
    print(text_anchor_html("lan", "Refined_dictionary.lan"))
