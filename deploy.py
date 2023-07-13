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
from util import fname2name
from datamodel import Annotator, span_templ
from create import tokenize_values

from flatvalues import flatten
from heatmap import render as heatmap


def mkdirs(vname="values-edited"):
    if not os.path.exists("site"):
        os.mkdir("site")
    for s in stemmers.keys():
        nxt = f"site/{s}"
        if not os.path.exists(nxt):
            os.mkdir(nxt)

        for c in corpora:
            nxt2 = f"{nxt}/{c}"
            if not os.path.exists(nxt2):
                os.mkdir(nxt2)


def values2css(stemmer: str, vname="values-edited") -> None:
    mapping: Dict[str, str] = {}
    with open(f"site/{stemmer}/{vname}.txt") as f:
        for i, l in enumerate(csv.reader(f)):
            mapping[l[0]] = cc.glasbey_cool[i]
    print(f"{stemmer}: {mapping}")
    with open(f"site/{stemmer}/values.css", "w") as fout:
        fout.writelines(
            "\n".join(f".{k} {{background-color: {v}}}" for k, v in mapping.items())
        )


tale_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../../style.css">
    <link rel="stylesheet" href="../values.css">
  </head>
<body><h1>{title}</h1>{body}</body></html>"""


def page(fname: str, stemmer: str) -> None:
    print(f"Reading: {fname}...")
    fname_path = fname.split(".")[0]
    fname_base = fname_path.split("/")[-1]
    fairytale = " ".join(fname_base.split("_")[1:])
    annotated = ""

    with open(fname) as fin:
        fulltext = fin.read()
    # print(fulltext)
    a = Annotator(stemmer, fulltext)
    annotated = a.rich_text()
    # print(annotated)
    fname_out = f"{fname_path}.html".replace("stories", f"site/{stemmer}")
    print(f"Writing: {fname_out}...")
    with open(fname_out, "w") as fout:
        fout.write(tale_templ.format(title=fairytale, body=annotated))


list_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="{root_path}style.css">
  </head>
<body><h3>{title}</h3>{body}</body></html>"""


def tale_list(stemmer: str, country: str = "", from_parent=False) -> str:
    """
    :param str country: Specifies corpus/country. If not set, will do for all
    :param bool from_parent: Specifies whether the generated file will be in the parent directory,
        so that URLs are adapted accordingly. This is not intended to be set manually
    """
    if not country:
        return "\n".join(tale_list(stemmer, c, True) for c in corpora)
    result = []
    names = {}
    for fname in glob(f"site/{stemmer}/{country}/*.html"):
        names[fname2name(fname)] = fname
    for name in sorted(names.keys()):
        fname = names[name]
        url = (
            fname.replace(f"site/{stemmer}/", "")
            if from_parent
            else fname.replace(f"site/{stemmer}/{country}/", "")
        )
        result += [f"<div><a href='{url}' target='fulltext'>{name}</a></div>"]
    return "\n".join(result)


def list_pages(stemmer: str):
    for country in corpora:
        fname_out = f"site/{stemmer}/{country}/index.html"
        with open(fname_out, "w") as fout:
            title = f"{country} Fairytales"
            listed = tale_list(stemmer, country)
            fout.write(list_templ.format(title=title, body=listed, root_path="../../"))
    fname_out = f"site/{stemmer}/index.html"
    with open(fname_out, "w") as fout:
        title = f"All Fairytales"
        listed = tale_list(stemmer)
        fout.write(list_templ.format(title=title, body=listed, root_path="../"))


values_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="values.css">
    <style>
.value {{
    line-height: 1.4em;
}}
    </style>
  </head>
<body><a href="map.html" target="_top">Tales vs Labels Heatmap</a><h3>{title}</h3>{body}</body></html>"""


def values_page(stemmer: str):
    title = "Values and Labels"
    result = []
    with open("values-edited.txt") as fin:
        for line in csv.reader(fin):
            if not line:
                continue
            stems = [stemmers[stemmer](v.strip().lower()) for v in line]
            result += [
                ", ".join(
                    [
                        span_templ.format(
                            id=s,
                            type=f"{s} {stems[0]}",
                            title=stems[0],
                            content=stems[0],
                        )
                        + line[0][len(stems[0]) :]
                    ]
                    + line[1:]
                )
            ]
    fname_out = f"site/{stemmer}/values.html"
    # body = "<p>" + "</p><p>".join(result) + "</p>"
    body = "<br/>".join(result)
    with open(fname_out, "w") as fout:
        listed = list(stemmer)
        fout.write(values_templ.format(title=title, body=body))


if __name__ == "__main__":
    mkdirs()

    shutil.copy("static/index.html", "site")
    shutil.copy("static/style.css", "site")

    flatten("values-edited.txt")

    # Generate CSS
    for s in stemmers.keys():
        heatmap(s, "values-edited.flat")
        tokenize_values(s)
        values2css(s)

    # Generate Fairy Tales
    for country in corpora:
        for fname in glob(f"stories/{country}/*.txt"):
            for s in stemmers.keys():
                page(fname, s)
    # # page("stories/Germany/160_A_Riddling_Tale.txt", "lan")

    # Generate Lists
    for s in stemmers.keys():
        list_pages(s)

    # Generate Values
    for s in stemmers.keys():
        values_page(s)
