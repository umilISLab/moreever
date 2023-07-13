#!/bin/python
"""Incrementally create a word embedding model"""

import os

import copy

from settings import model_dir
from corpora import corpora as corpora
from stemmers import stemmers
from algo import algos

from util import collect_tokens
from create import tokenize_values, load_source, calc_occurences, annotate_occurences


def create_models(tkn="sb", algo="w2v", epochs=200):
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)

    _, valuesbackref = tokenize_values(tkn)
    # _, tokenized = load_source(stemmers["dummy"], corpora)
    _, tokenized = load_source(stemmers[tkn], corpora)
    # occurences, occurences_tv, occurences_backref = calc_occurences(values, tokenized)
    tokenized = annotate_occurences(tokenized, valuesbackref, tkn)

    all_tokens = collect_tokens(tokenized)
    print(f"all tokens: {sum(len(x) for x in all_tokens)}")
    model = algos[algo](
        sentences=all_tokens,
        vector_size=300,
        window=8,
        min_count=40,
        workers=6,
        epochs=epochs,
    )

    # base/compass model
    i = 0
    name_templ = "{model_dir}/all.{tkn}.e{epochs}.{algo}.{i}"
    base_name = name_templ.format(
        model_dir=model_dir, tkn=tkn, epochs=epochs, algo=algo, i=i
    )
    while os.path.exists(base_name):
        i += 1
        base_name = name_templ.format(
            model_dir=model_dir, tkn=tkn, epochs=epochs, algo=algo, i=i
        )
    print(base_name)
    model.save(base_name)

    # per-corpus models
    corpora_tokens = []
    for c in tokenized.keys():
        p = collect_tokens(tokenized, c)
        print(f"{c} tokens (post annotation): {sum(len(x) for x in p)}")
        corpora_tokens += [p]
        m = copy.deepcopy(model)
        m.train(p, epochs=m.epochs, total_examples=m.corpus_count)
        m.save(base_name.replace("all", c))


if __name__ == "__main__":
    # tkn = "ps"
    # tkn = "wnl"
    # tkn = 'dummy'
    # tkn = "lan"
    tkn = "sb"

    epochs = 200

    algo = "w2v"
    # algo = "ft"

    create_models(tkn, algo)
