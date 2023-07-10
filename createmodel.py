#!/bin/python
"""Incrementally create a word embedding model"""

import os

import copy

from const import countries as corpora
from stemmers import stemmers
from algo import algos

from util import story_tokenize, collect_tokens
from create import tokenize_values, load_source, calc_occurences, annotate_occurences


# tkn = "ps"
tkn = "wnl"
# tkn = 'dummy'
# tkn = "lan"
# tkn = "sb"

epochs = 200

algo = "w2v"
# algo = "ft"

model_dir = "/home/mapto/models/20230710"

values, valuesbackref = tokenize_values(tkn)
fulltexts, tokenized = load_source(stemmers[tkn], corpora)
occurences, occurences_tv, occurences_backref = calc_occurences(values, tokenized)
tokenized = annotate_occurences(tokenized, valuesbackref)

all_tokens = collect_tokens(tokenized)
print(f"tokens: {sum(len(x) for x in all_tokens)}")
model = algos[algo](
    sentences=all_tokens,
    vector_size=300,
    window=8,
    min_count=40,
    workers=6,
    epochs=epochs,
)
# model

p1 = collect_tokens(tokenized, "G")
p2 = collect_tokens(tokenized, "I")
p3 = collect_tokens(tokenized, "P")
print(f"German tokens (post annotation): {sum(len(x) for x in p1)}")
print(f"Italian tokens (post annotation): {sum(len(x) for x in p2)}")
print(f"Portuguese tokens (post annotation): {sum(len(x) for x in p3)}")

M1 = copy.deepcopy(model)
M1.train(p1, epochs=M1.epochs, total_examples=M1.corpus_count)

M2 = copy.deepcopy(model)
M2.train(p2, epochs=M2.epochs, total_examples=M2.corpus_count)

M3 = copy.deepcopy(model)
M3.train(p3, epochs=M3.epochs, total_examples=M3.corpus_count)

i = 0
name_templ = "{model_dir}/M0.{tkn}.e{epochs}.{algo}.{i}"
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

m1_name = base_name.replace("M0", "M1")
M1.save(m1_name)

m2_name = base_name.replace("M0", "M2")
M2.save(m2_name)

m3_name = base_name.replace("M0", "M3")
M3.save(m3_name)
