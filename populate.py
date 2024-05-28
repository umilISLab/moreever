#!/usr/bin/env python3
"""Populates the database.
To be executed standalone before using the application.

Usage:
  populate.py -l
  populate.py <stemmer>

Options:
  -h --help             This information
  -l --list             List available stemmers
  --version             Print version

"""
__version__ = "0.0.1"

from docopt import docopt  # type: ignore

import os
from glob import glob

from db import Base, engine, Session

from customtypes import FulltextsMap, TokenizedMap
from settings import VOCAB, CORPORA, LANG
from stemmers import stemmers
from corpora import corpora as global_corpora

from util import rmdirs, mkdirs, story_tokenize, fname2name
from model import Token, Text, Annotation, Sentence, Word

from flatvalues import flatten


def drop_tokenized_values(s: Session, stemmer: str) -> None:
    data = s.query(Token).where(Token.stemmer == stemmer).delete()
    # s.delete(data)
    s.commit()


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
            stemmed_fitems = [token_func(x, None) for x in fitems]
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


def drop_source(s: Session, stemmer: str):
    texts = s.query(Text).join(Sentence, Sentence.text_id == Text.id).join(Word, Word.sentence_id == Sentence.id).where(Word.stemmer == stemmer).all()
    for t in texts:
        s.delete(t)
    sents = s.query(Sentence).join(Word, Word.sentence_id == Sentence.id).where(Word.stemmer == stemmer).all()
    for sent in sents:
        s.delete(sent)
    s.query(Word).where(Word.stemmer == stemmer).delete()
    s.commit()


def load_source(
    s: Session, corpus: str, fname: str, stemmer="dummy", corpora: list[str] = []
):
    """loads the sources from the specified directory structure

    Args:
        token_func (_type_): the used stemmer as a function. Defaults to None leads to use of dummy stemmer.
        corpora (List[str]): a list of subdirectories. Corresponds to corpora.corpora.
        Defaults to empty list, which leads to reading all subdirectories of corpora/

    Returns:
        Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]: returns two dictionaries:
            corpora->text_name->fulltext and corpora->text_name->list of tokenized sentences
    """
    with open(fname) as f:
        # print("=============== " + fname)
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
        # print(content)
        tokenized = story_tokenize(content)
        # print(tokenized)
        for i, sentence in enumerate(tokenized):
            s_text = " ".join(sentence)
            sent = Sentence(order=i, text_id=txt.id, sentence=s_text)
            s.add(sent)
            s.flush()
            s.add_all(
                [
                    Word(
                        word=word,
                        order=j,
                        sentence_id=sent.id,
                        stemmer=stemmer,
                        token=stemmers[stemmer](word, None),
                    )
                    for j, word in enumerate(sentence)
                ]
            )
    s.commit()


if __name__ == "__main__":
    args = docopt(__doc__, version=__version__)

    # print(args)

    if "--list" in args and args["--list"]:
        print(f"Available stemmers for '{LANG}':")
        print("\n".join(stemmers))
        exit(0)

    stem = args["<stemmer>"]

    Base.metadata.create_all(engine)
    s = Session()

    rmdirs()
    mkdirs()

    drop_tokenized_values(s, stem)
    drop_source(s, stem)

    print(f">>> TOKENIZE VALUES with {stem}")
    tokenize_values(s, stem)

    for corpus in global_corpora:
        for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
	    print(f">>> TOKENIZE {fname} with {stem}")
            load_source(s, corpus, fname, stem)

    # for stem in stemmers:
    #     print(stem)
    #     # print("=============== TOKENIZE VALUES")
    #     tokenize_values(s, stem)

    #     for corpus in global_corpora:
    #         for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
    #             load_source(s, corpus, fname, stem)

    #     # corpus = "1_full"
    #     # for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
    #     #     load_source(s, corpus, fname, stem)

    #     # corpus = "2_consolidated"
    #     # for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
    #     #     load_source(s, corpus, fname, stem)

    #     # corpus = "3_majority"
    #     # for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
    #     #     load_source(s, corpus, fname, stem)

    #     # corpus = "4_split"
    #     # for fname in glob(f"./corpora.{CORPORA}/{corpus}/*.txt"):
    #     #     load_source(s, corpus, fname, stem)
