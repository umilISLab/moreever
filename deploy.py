#!/bin/python
"""This generates a static website.
"""


from typing import Dict, List

import os
import shutil
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
from create import tokenize_values, load_source, calc_occurences

from flatvalues import flatten
from heatmap import render as heatmap
from keywords import render as keywords_venn


def rmdirs():
    for s in stemmers.keys():
        stem_dir = f"site/{s}"
        if os.path.exists(stem_dir):
            shutil.rmtree(stem_dir)


def mkdirs(vname="values-edited"):
    if not os.path.exists("site"):
        os.mkdir("site")
    for s in stemmers.keys():
        nxt = f"site/{s}"
        if not os.path.exists(nxt):
            os.mkdir(nxt)
        nxt3 = f"{nxt}/values"
        if not os.path.exists(nxt3):
            os.mkdir(nxt3)

        for c in corpora:
            nxt2 = f"{nxt}/{c}"
            if not os.path.exists(nxt2):
                os.mkdir(nxt2)
            nxt3 = f"{nxt2}/values"
            if not os.path.exists(nxt3):
                os.mkdir(nxt3)


def values2css(stemmer: str, vname="values-edited") -> None:
    mapping: Dict[str, str] = {}
    with open(f"site/{stemmer}/{vname}.txt") as f:
        for i, l in enumerate(csv.reader(f)):
            mapping[l[0]] = cc.glasbey_cool[i]
    print(f"Styles for {stemmer}: {mapping}")
    with open(f"site/{stemmer}/values.css", "w") as fout:
        fout.writelines(
            "\n".join(f".{k} {{background-color: {v}}}" for k, v in mapping.items())
        )


def page(fname: str, stemmer: str, values_br: Dict[str, str] = {}) -> None:
    # print(f"Reading: {fname}...")
    fname_path = fname.split(".")[0]
    fname_base = fname_path.split("/")[-1]
    fairytale = " ".join(fname_base.split("_")[1:])
    annotated = ""

    with open(fname) as fin:
        fulltext = fin.read()
    # print(fulltext)
    a = Annotator(stemmer, fulltext, values_br)
    annotated = a.rich_text()
    # print(annotated)
    fname_out = f"{fname_path}.html".replace("stories", f"site/{stemmer}")
    print(f"Writing: {fname_out}...")
    with open(fname_out, "w") as fout:
        fout.write(tale_templ.format(title=fairytale, body=annotated))


def tale_dict(stemmer: str, country: str) -> Dict[str, str]:
    names = {}
    for fname in glob(f"site/{stemmer}/{country}/*.html"):
        names[fname2name(fname)] = fname
    return names


def tale_html(stemmer: str, country: str = "", from_parent=False) -> str:
    """
    :param str country: Specifies corpus/country. If not set, will do for all
    :param bool from_parent: Specifies whether the generated file will be in the parent directory,
        so that URLs are adapted accordingly. This is not intended to be set manually
    """
    if not country:
        return "\n".join(tale_html(stemmer, c, True) for c in corpora)
    names = tale_dict(stemmer, country)
    result = []
    for name in sorted(names.keys()):
        fname = names[name]
        url = (
            fname.replace(f"site/{stemmer}/", "")
            if from_parent
            else fname.replace(f"site/{stemmer}/{country}/", "")
        )
        result += [f"<div><a href='{url}' target='fulltext'>{name}</a></div>"]
    return "\n".join(result)


def value_list_html(
    occurences_backref: Dict[str, Dict[str, int]],
    stemmer: str,
    label: str,
    country: str = "",
    from_parent=False,
):
    if not country:
        return "\n".join(
            value_list_html(occurences_backref, stemmer, label, c, True)
            for c in corpora
        )
    all_tales = tale_dict(stemmer, country)
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
        url = fname.replace(f"site/{stemmer}/", f"../" if from_parent else "")
        result += [f"<div><a href='{url}' target='fulltext'>{name}</a></div>"]
    return "\n".join(result)


def value_list_page(
    occurences_backref: Dict[str, Dict[str, int]], stemmer: str, label: str = ""
):
    # per-corpus list
    for country in corpora:
        listed = value_list_html(occurences_backref, stemmer, label, country)
        # print(listed)
        if not listed.strip():
            continue
        fname_out = f"site/{stemmer}/{country}/values/{label}.html"
        with open(fname_out, "w") as fout:
            title = f"{country} Fairytales [{label}]"
            fout.write(
                list_templ.format(title=title, body=listed, root_path="../../../")
            )

    # all-corpus list
    listed = value_list_html(occurences_backref, stemmer, label)
    if not listed.strip():
        return
    fname_out = f"site/{stemmer}/values/{label}.html"
    with open(fname_out, "w") as fout:
        title = f"All Fairytales [{label}]"
        fout.write(list_templ.format(title=title, body=listed, root_path="../../"))


def value_list_pages(
    stemmer: str,
    values: Dict[str, List[str]] = {},
    values_backref: Dict[str, str] = {},
    tokenized: Dict[str, Dict[str, List[List[str]]]] = {},
    occurences_backref: Dict[str, Dict[str, int]] = {},
):
    """Generation of list (left-hand side) per value. Works with all files in site/<stemmer>/<corpus>/*.html,
    so make sure tu run it before list_pages() which generates an index file in those directories.
    """
    if not values or not values_backref or not tokenized or not occurences_backref:
        values, values_backref = tokenize_values(stemmer, fname="values-edited.flat")
        _, tokenized = load_source(stemmers[stemmer], corpora)
        _, _, occurences_backref = calc_occurences(values, tokenized)

    print(f"For {stemmer}: {len(values_backref)} labels")
    for l in values_backref.keys():
        if l not in occurences_backref:
            continue
        # print(
        #     f"Occurrences of {l} with {stemmer}: {sum(v for v in occurences_backref[l].values())} in {len(occurences_backref[l])} texts."
        # )
        value_list_page(occurences_backref, stemmer, l)


def list_pages(stemmer: str):
    """The page containing a list of tales. See list_templ for reference.
    Generates an index file in site/<stemmer> and site/<stemmer>/<corpus>,
    so if any code reads list of texts as files, make sure to run it before this."""
    # per-corpus list
    for country in corpora:
        fname_out = f"site/{stemmer}/{country}/index.html"
        with open(fname_out, "w") as fout:
            title = f"{country} Fairytales"
            listed = tale_html(stemmer, country)
            fout.write(list_templ.format(title=title, body=listed, root_path="../../"))

    # all-corpus list
    fname_out = f"site/{stemmer}/index.html"
    with open(fname_out, "w") as fout:
        title = f"All Fairytales"
        listed = tale_html(stemmer)
        fout.write(list_templ.format(title=title, body=listed, root_path="../"))


def values_page(stemmer: str):
    """The page that list all the values, see values_templ for reference"""
    title = "Values and Labels"
    result = []
    with open("values-edited.txt") as fin:
        for line in csv.reader(fin):
            if not line:
                continue
            stems = [stemmers[stemmer](v.strip().lower()) for v in line]
            links = []
            for i, s in enumerate(stems):
                found = os.path.exists(f"site/{stemmer}/values/{s}.html")
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
                        url=f"/{stemmer}/values/{s}.html",
                        type=f"{stemmer}",
                        title=title,
                        content=styled,
                    )
                    if found
                    else styled
                )
                links += [linked]
            result += [", ".join(links)]
    fname_out = f"site/{stemmer}/values.html"
    # body = "<p>" + "</p><p>".join(result) + "</p>"
    body = "<br/>".join(result)
    with open(fname_out, "w") as fout:
        fout.write(values_templ.format(title=title, body=body))


if __name__ == "__main__":
    rmdirs()
    mkdirs()

    shutil.copy("static/index.html", "site")
    shutil.copy("static/style.css", "site")

    flatten("values-edited.txt")

    # Generate CSS
    for s in stemmers.keys():
        _1, values_br = tokenize_values(s)
        values_flat, values_br_flat = tokenize_values(s, "values-edited.flat")
        _2, tokenized = load_source(stemmers[s], corpora)
        if s == "morph":
            from morphroot import save_roots

            save_roots()
        occ_flat, occ_tv_flat, occ_br_flat = calc_occurences(values_flat, tokenized)

        heatmap(
            s,
            values=values_flat,
            tokenized=tokenized,
            occurences=occ_flat,
            occurences_backref=occ_br_flat,
        )
        keywords_venn(
            s, values=values_flat, tokenized=tokenized, occurences_tv=occ_tv_flat
        )
        values2css(s)

        # Generate Fairy Tales
        for country in corpora:
            for fname in glob(f"stories/{country}/*.txt"):
                page(fname, s, values_br)

        # Generate Lists
        value_list_pages(
            s,
            values=values_flat,
            values_backref=values_br_flat,
            tokenized=tokenized,
            occurences_backref=occ_br_flat,
        )
        list_pages(s)

        # Generate Values
        values_page(s)
