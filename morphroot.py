#!/bin/python
from typing import Dict

from settings import db_dir, CORPORA
import os
import csv

from morphemes import Morphemes  # type: ignore

morph_dir = f"{db_dir}/morphemes"
morph_data = f"{morph_dir}/roots.csv"

if not os.path.exists(morph_dir):
    os.mkdir(morph_dir)
m = Morphemes(morph_dir)

roots: Dict[str, str] = {}


def load_roots():
    if os.path.exists(morph_data):
        with open(morph_data, "r") as f:
            for r in csv.reader(f):
                assert r[0] not in roots
                roots[r[0]] = r[1]
        print(f"Loaded {len(roots)} morphemens")


def save_roots():
    with open(morph_data, "w") as f:
        writer = csv.writer(f)
        writer.writerows((k, roots[k]) for k in sorted(list(roots.keys())))


def extract_root(word, tree):
    result = ""
    # print(word)
    for e in tree:
        if e["type"] == "root":
            # assert not result, f'Found at least two roots for {word}: {result} and {e["text"]}'
            result += e["text"]
        if "children" in e:
            # value = get_root_morpheme(word, e["children"])
            # assert not result, f'Found at least two roots for {word}: {result} and {value}'
            result += extract_root(word, e["children"])
    roots[word] = result
    return result


def get_root_morpheme(word: str) -> str:
    if not roots:
        load_roots()
    word = word.lower()
    if word in roots:
        return roots[word]
    if not word.isalpha():
        roots[word] = word
        return word
    tree = m.parse(word.lower()).get("tree")
    if not tree:
        roots[word] = word
        return word
    return extract_root(word, tree)  # if word.isalpha()    else word.lower()


if __name__ == "__main__":
    from glob import glob
    from util import story_tokenize
    from corpora import corpora

    for corpus in corpora:
        for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
            print(fname)
            with open(fname) as f:
                # talename = fname.split("/")[-1].split(".")[-2]
                fulltext = "".join(f.readlines())
                story_tokenize(get_root_morpheme, fulltext)
            save_roots()
