""" General functions with dependence on data model"""

from glob import glob

from settings import CORPORA

from corpora import corpora

from datamodel import Annotator


def get_fulltexts() -> dict[str, dict[str, str]]:
    """as done in create.load_source()"""
    fulltexts: dict[str, dict[str, str]] = {}
    for corpus in corpora:
        fulltexts[corpus] = {}
        for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
            with open(fname) as f:
                textname = fname.split("/")[-1].split(".")[-2]
                assert textname, f"Seems not to contain file name: {fname}"
                fulltexts[corpus][textname] = "".join(f.readlines())
    # print(fulltexts)
    return fulltexts


def corpora_tokens() -> dict[str, dict[str, list[str]]]:
    fulltexts = get_fulltexts()
    tokens: dict[str, dict[str, list[str]]] = {}
    for c, texts in fulltexts.items():
        tokens[c] = {}
        for t, fulltext in texts.items():
            tokens[c][fulltext] = []
            # stemmer ignored
            a = Annotator("dummy", fulltext)
            for paragraph in fulltext.split("\n"):
                # tokens[c][fulltext] += [sentence for sentence in a.tokens(paragraph)]
                tokens[c][fulltext] += [
                    token for sentence in a.tokens(paragraph) for token in sentence
                ]
    return tokens
