#!/bin/python
"""This generates a static website.
"""


from typing import Dict, List

import os
import shutil
from glob import glob

from corpora import corpora
from stemmers import stemmers
from template import list_templ

from create import tokenize_values, load_source, calc_occurences

from flatvalues import flatten
from heatmap import render as heatmap
from keywords import keywords_venn, clusters_venn

from pages import values_html, tale_html, value_list_html, page_html
from pages import values_css


def rmdirs():
    for s in stemmers.keys():
        stem_dir = f"site/{s}"
        if os.path.exists(stem_dir):
            shutil.rmtree(stem_dir)


def mkdirs():
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
    with open(f"site/{stemmer}/values.css", "w") as fout:
        fout.writelines(values_css(stemmer, vname))


def page(fname: str, stemmer: str, values_br: Dict[str, str] = {}) -> None:
    fname_path = fname.split(".")[0]
    fname_out = f"{fname_path}.html".replace("stories", f"site/{stemmer}")
    print(f"Writing: {fname_out}...")
    with open(fname_out, "w") as fout:
        fout.write(page_html(fname, stemmer, values_br))


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
    fname_out = f"site/{stemmer}/values.html"
    with open(fname_out, "w") as fout:
        fout.write(values_html(stemmer))


if __name__ == "__main__":
    rmdirs()
    mkdirs()

    shutil.copy("static/index.html", "site")
    shutil.copy("static/style.css", "site")

    flatten("values-edited.txt")

    # Generate CSS
    for tkn in stemmers.keys():
        values, values_br = tokenize_values(tkn)
        values_flat, values_br_flat = tokenize_values(tkn, "values-edited.flat")
        _2, tokenized = load_source(stemmers[tkn], corpora)
        if tkn == "morph":
            from morphroot import save_roots

            save_roots()
        occ, occ_tv, occ_br = calc_occurences(values, tokenized)
        occ_flat, occ_tv_flat, occ_br_flat = calc_occurences(values_flat, tokenized)

        with open(f"site/{tkn}/map.html", "w") as f:
            f.writelines(
                heatmap(
                    tkn,
                    values=values_flat,
                    tokenized=tokenized,
                    occurences=occ_flat,
                    occurences_backref=occ_br_flat,
                )
            )
        with open(f"site/{tkn}/keywords.svg", "w") as f:
            f.writelines(
                keywords_venn(
                    tkn,
                    values=values_flat,
                    tokenized=tokenized,
                    occurences_tv=occ_tv_flat,
                )
            )
        for value, diag_file in clusters_venn(
            tkn=tkn, values=values, occurences_tv=occ_tv
        ).items():
            with open(f"site/{tkn}/cluster-{value}.svg", "w") as f:
                f.writelines(diag_file)

        values2css(tkn)

        # Generate Fairy Tales
        for country in corpora:
            for fname in glob(f"stories/{country}/*.txt"):
                page(fname, tkn, values_br)

        # Generate Lists
        value_list_pages(
            tkn,
            values=values_flat,
            values_backref=values_br_flat,
            tokenized=tokenized,
            occurences_backref=occ_br_flat,
        )
        list_pages(tkn)

        # Generate Values
        values_page(tkn)
