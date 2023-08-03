#!/usr/bin/env python3
"""A dynamic service for moreever. See github.com/umilISLab/moreever/ for details."""
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from corpora import corpora
from stemmers import stemmers
from template import list_templ

from create import tokenize_values, load_source, calc_occurences
from pages import values_html, tale_html, value_list_html, page_html
from pages import values_css
from keywords import keywords_venn, clusters, render_venn, filter_clusters_containing
from heatmap import render as heatmap_render


class CSSResponse(Response):
    media_type = "text/css"


class SVGResponse(Response):
    media_type = "image/svg+xml"


app = FastAPI(
    title="moreever",
    description=__doc__,
    # docs_url="/",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # needed for Basic Auth
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/{stemmer}/values.css", response_class=CSSResponse)
async def values_css_page(stemmer: str):
    return values_css(stemmer)


@app.get("/{stemmer}/values.html", response_class=HTMLResponse)
async def values_page(stemmer: str):
    return values_html(stemmer)


@app.get("/{stemmer}/keywords.svg", response_class=SVGResponse)
async def keywords_venn_page(stemmer: str):
    return keywords_venn(stemmer, fname="values-edited.flat")


@app.get("/{stemmer}/cluster-{value}.svg", response_class=SVGResponse)
async def cluster_venn_page(stemmer: str, value: str):
    values, _ = tokenize_values(stemmer, fname="values-edited")
    _, tokenized = load_source(stemmers[stemmer], corpora)
    _, occurences_tv, _ = calc_occurences(values, tokenized)
    cl = clusters(stemmer, values=values, occurences_tv=occurences_tv)
    per_corpus = {c: filter_clusters_containing(cl[c], value) for c in corpora}
    print(per_corpus)
    # if exactly one cluster per corpus contains the value
    if len([k for k, v in per_corpus.items() if len(v) == 1]) != 3:
        raise HTTPException(
            status_code=409,
            detail=f"Cluster does not have representatives in all three corpora: {[k for k, v in per_corpus.items() if len(v) == 1]}",
        )
    return render_venn({k: set(v.pop()) for k, v in per_corpus.items()})


@app.get("/{stemmer}/map.html", response_class=HTMLResponse)
async def heatmap_page(stemmer: str):
    return heatmap_render(stemmer, fname="values-edited.flat")


# @app.get("/{stemmer}", response_class=HTMLResponse)
@app.get("/{stemmer}/index.html", response_class=HTMLResponse)
# @app.get("/{stemmer}", response_class=HTMLResponse)
@app.get("/{stemmer}/{corpus}/index.html", response_class=HTMLResponse)
async def values_index(stemmer: str, corpus: str = ""):
    if corpus:
        if corpus not in corpora:
            raise HTTPException(
                status_code=404, detail=f"Corpus not found for {corpus}"
            )
        title = f"{corpus} Fairytales"
        listed = tale_html(stemmer, corpus)
        return list_templ.format(title=title, body=listed, root_path="../../")

    title = f"All Fairytales"
    listed = tale_html(stemmer)
    return list_templ.format(title=title, body=listed, root_path="../")


@app.get("/{stemmer}/values/{label}.html", response_class=HTMLResponse)
@app.get("/{stemmer}/{corpus}/values/{label}.html", response_class=HTMLResponse)
async def value_list_page(stemmer: str, label: str, corpus: str = ""):
    if corpus:
        if corpus not in corpora:
            raise HTTPException(
                status_code=404, detail=f"Corpus not found for {corpus}"
            )
        values, _ = tokenize_values(stemmer, fname="values-edited.flat")
        _, tokenized = load_source(stemmers[stemmer], corpora)
        _, _, occurences_backref = calc_occurences(values, tokenized)
        listed = value_list_html(occurences_backref, stemmer, label, corpus)
        # print(listed)
        if not listed.strip():
            raise HTTPException(
                status_code=404,
                detail=f"List not found for {label} in {corpus} with {stemmer}",
            )
        title = f"{corpus} Fairytales [{label}]"
        return list_templ.format(title=title, body=listed, root_path="../../../")

    values, _ = tokenize_values(stemmer, fname="values-edited.flat")
    _, tokenized = load_source(stemmers[stemmer], corpora)
    _, _, occurences_backref = calc_occurences(values, tokenized)
    listed = value_list_html(occurences_backref, stemmer, label)
    if not listed.strip():
        raise HTTPException(
            status_code=404, detail=f"List not found for {label} with {stemmer}"
        )
    title = f"All Fairytales [{label}]"
    return list_templ.format(title=title, body=listed, root_path="../../")


@app.get("/{stemmer}/{corpus}/{talename}.html", response_class=HTMLResponse)
async def page(stemmer: str, corpus: str, talename: str):
    fname = f"stories/{corpus}/{talename}.txt"
    _, values_br = tokenize_values(stemmer, fname="values-edited")
    return page_html(fname, stemmer, values_br)


app.mount("", StaticFiles(directory="./static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run("main:app", reload=True)
