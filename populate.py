#!/usr/bin/env python3
"""Populates the database.
To be executed standalone before using the application."""
import os
from glob import glob

from db import Base, engine, Session

from customtypes import FulltextsMap, TokenizedMap
from settings import VOCAB, CORPORA
from stemmers import stemmers
from corpora import corpora as global_corpora

from util import rmdirs, mkdirs, story_tokenize, fname2name
from model import Token, Text, Annotation, Sentence, Word

from flatvalues import flatten


def tokenize_values(s: Session, stemmer: str, vocab: str = "") -> None:
    token_func = stemmers[stemmer]
    if not vocab:
        vocab = VOCAB
    if vocab.endswith(".flat") and not os.path.exists(f"vocab/{vocab}.csv"):
        flatten(f"vocab/{vocab[:-5]}.csv")
    outlines = []
    with open(f"vocab/{vocab}.csv") as f:
        flines = f.readlines()
        for l in flines:
            if not l.strip():
                continue
            token_class = l.split(",")[0]
            fitems = [x.strip().lower() for x in l.split(",") if x.strip()]
            stemmed_fitems = [token_func(x) for x in fitems]
            s.add_all(
                [
                    Token(token=token, stemmer=stemmer, token_class=token_class)
                    for token in stemmed_fitems
                ]
            )
            outlines += [",".join(stemmed_fitems) + "\n"]
    s.commit()

    with open(f"vocab/{stemmer}/{vocab}.csv", "w") as fout:
        # fout.write("\n".join(stemmed_fitems))
        fout.writelines(outlines)


def load_source(s: Session, stemmer="dummy", corpora: list[str] = []):
    """loads the sources from the specified directory structure

    Args:
        token_func (_type_): the used stemmer as a function. Defaults to None leads to use of dummy stemmer.
        corpora (List[str]): a list of subdirectories. Corresponds to corpora.corpora.
        Defaults to empty list, which leads to reading all subdirectories of corpora/

    Returns:
        Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]: returns two dictionaries:
            corpora->text_name->fulltext and corpora->text_name->list of tokenized sentences
    """
    if not corpora:
        corpora = global_corpora

    for corpus in corpora:
        for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
            with open(fname) as f:
                textname = fname.split("/")[-1].split(".")[-2]
                assert textname, f"Seems not to contain file name: {fname}"
                content = "".join(f.readlines())
                txt = Text(
                    fname=textname,
                    name=fname2name(textname),
                    corpus=corpus,
                    fulltext=content,
                )
                s.add(txt)
                s.flush()
                tokenized = story_tokenize(stemmers[stemmer], content)
                for i, sentence in enumerate(tokenized):
                    s_text = " ".join(sentence)
                    sent = Sentence(order=i, text_id=txt.id, sentence=s_text)
                    s.add(sent)
                    s.flush()
                    s.add_all(
                        [
                            Word(
                                word=word, order=j, sentence_id=sent.id, stemmer=stemmer
                            )
                            for j, word in enumerate(sentence)
                        ]
                    )
    s.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    s = Session()

    rmdirs()
    mkdirs()
    for stem in stemmers:
        print(stem)
        tokenize_values(s, stem)
        load_source(s, stem)
