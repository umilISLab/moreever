#!/usr/bin/env python3
"""A dynamic service for moreever. See https://github.com/umilISLab/moreever/ for details."""
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from corpora import corpora
from stemmers import stemmers
from template import list_templ

from create import tokenize_values, load_source, calc_occurences
from pages import index_html, page_text_html, page_corpus_html
from pages import text_html, values_html, value_list_html
from pages import values_css
from keywords import keywords_venn, clusters, render_venn, filter_clusters_containing
from heatmap import render as heatmap_render

from settings import DEBUG


class CSSResponse(Response):
    media_type = "text/css"


class SVGResponse(Response):
    media_type = "image/svg+xml"


app = FastAPI(
    title="moreever",
    description=__doc__,
    # docs_url="/",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # needed for Basic Auth
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/{stemmer}/{vocab}/values.css", response_class=CSSResponse)
async def values_css_page(vocab: str, stemmer: str):
    """The CSS providing the coloring for the vocabulary."""
    return values_css(stemmer, vocab)


@app.get("/{stemmer}/{vocab}/values.html", response_class=HTMLResponse)
async def values_page(vocab: str, stemmer: str):
    """The coloured vocabularly."""
    return values_html(stemmer, vocab)


@app.get("/{stemmer}/{vocab}/keywords.svg", response_class=SVGResponse)
async def keywords_venn_page(vocab: str, stemmer: str):
    """The Venn diagram with the vocabulary"""
    return keywords_venn(stemmer, f"{vocab}.flat")


@app.get("/{stemmer}/{vocab}/cluster-{value}.svg", response_class=SVGResponse)
async def cluster_venn_page(vocab: str, stemmer: str, value: str):
    """The Venn diagram with the word vectors"""
    values, _ = tokenize_values(stemmer, vocab)
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


@app.get("/{stemmer}/{vocab}/map.html", response_class=HTMLResponse)
async def heatmap_page(stemmer: str, vocab: str):
    """The Heatmap with texts vs labels"""
    return heatmap_render(stemmer, f"{vocab}.flat")


# @app.get("/{stemmer}", response_class=HTMLResponse)
@app.get("/{stemmer}/{vocab}/index.html", response_class=HTMLResponse)
# @app.get("/{stemmer}", response_class=HTMLResponse)
@app.get("/{stemmer}/{vocab}/{corpus}/index.html", response_class=HTMLResponse)
async def values_index(stemmer: str, vocab: str, corpus: str = ""):
    """The list of texts in the corpus (or in all corpora if corpus unspecified)"""
    # print(corpus)
    if corpus:
        if corpus not in corpora:
            raise HTTPException(
                status_code=404, detail=f"Corpus not found for {corpus}"
            )
        title = f"{corpus} Texts"
        listed = text_html(stemmer, vocab, corpus)
        return list_templ.format(title=title, body=listed, root_path="../../../")

    title = f"All Texts"
    listed = text_html(stemmer, vocab)
    return list_templ.format(title=title, body=listed, root_path="../../")


@app.get("/{stemmer}/{vocab}/values/{label}.html", response_class=HTMLResponse)
@app.get("/{stemmer}/{vocab}/{corpus}/values/{label}.html", response_class=HTMLResponse)
async def value_list_page(stemmer: str, vocab: str, label: str, corpus: str = ""):
    if corpus:
        if corpus not in corpora:
            raise HTTPException(
                status_code=404, detail=f"Corpus not found for {corpus}"
            )
        values, _ = tokenize_values(stemmer, f"{vocab}.flat")
        _, tokenized = load_source(stemmers[stemmer], corpora)
        _, _, occurences_backref = calc_occurences(values, tokenized)
        listed = value_list_html(occurences_backref, stemmer, vocab, label, corpus)
        # print(listed)
        if not listed.strip():
            raise HTTPException(
                status_code=404,
                detail=f"List not found for {label} in {corpus} with {stemmer}",
            )
        title = f"{corpus} Texts [{label}]"
        return list_templ.format(title=title, body=listed, root_path="../../../../")

    values, _ = tokenize_values(stemmer, f"{vocab}.flat")
    _, tokenized = load_source(stemmers[stemmer], corpora)
    _, _, occurences_backref = calc_occurences(values, tokenized)
    listed = value_list_html(occurences_backref, vocab, stemmer, label)
    if not listed.strip():
        raise HTTPException(
            status_code=404, detail=f"List not found for {label} with {stemmer}"
        )
    title = f"All Texts [{label}]"
    return list_templ.format(title=title, body=listed, root_path="../../../")


@app.get("/{stemmer}/{vocab}/{corpus}/{textname}.html", response_class=HTMLResponse)
async def page_text(stemmer: str, vocab: str, corpus: str, textname: str):
    fname = f"corpora/{corpus}/{textname}.txt"
    _, values_br = tokenize_values(stemmer, vocab)
    return page_text_html(fname, stemmer, vocab, values_br)


@app.get("/{stemmer}/{vocab}/{corpus}.html", response_class=HTMLResponse)
async def page_corpus(stemmer: str, vocab: str, corpus: str, textname: str):
    # TODO
    _, values_br = tokenize_values(stemmer, vocab)
    return page_corpus_html(corpus, stemmer, vocab, values_br)


@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def index():
    return index_html()


app.mount("", StaticFiles(directory="./static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run("main:app", reload=True, log_level=10 if DEBUG else 30)
