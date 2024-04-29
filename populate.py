#!/usr/bin/env python3
"""Populates the database.
To be executed standalone before using the application."""
import os
from glob import glob

from db import Base, engine, Session

from customtypes import FulltextsMap, TokenizedMap
from settings import VOCAB
from stemmers import stemmers
from corpora import corpora as global_corpora

from util import rmdirs, mkdirs, story_tokenize
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
        for fname in glob(f"./corpora/{corpus}/*.txt"):
            with open(fname) as f:
                textname = fname.split("/")[-1].split(".")[-2]
                assert textname, f"Seems not to contain file name: {fname}"
                content = "".join(f.readlines())
                txt = Text(name=textname, corpus=corpus, fulltext=content)
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

def calc_occurences(
    values: dict[str, list[str]],
    tokenized: dict[str, dict[str, list[list[str]]]],
    func_name="dummy",
) -> tuple[
    dict[tuple[str, str], int], dict[str, dict[str, int]], dict[str, dict[str, int]]
]:
    """_Calculate occurences of words_

    Args:
        values (Dict[str, List[str]]): the dictionary mapping values to list of synonym labels, e.g. produced by tokenize_values()
        tokenized (Dict[str, Dict[str, List[List[str]]]]): the tokenized text content, produced by load_source()
        func_name (str, optional): The used stemmer, notice that stemmer is an idempotent function,
        i.e. applying it twice produces the same result. Defaults to "dummy".

    Returns:
        Tuple[ Dict[Tuple[str, str], int], Dict[str, Dict[str, int]], Dict[str, Dict[str, int]] ]: returns three counting dictionaries:
            (text_name, value): count, text_name: (value: count), value: (text_name: count),
            where text_name is in the format <corpus>/<chapter>_<text> (no extension)
    """
    # print(tokenized)
    token_func = stemmers[func_name]
    occurences: dict[tuple[str, str], int] = {}  # (text_name, value): count)
    occurences_tv: dict[str, dict[str, int]] = {}  # text_name: (value: count)
    occurences_backref: dict[str, dict[str, int]] = {}  # value: (text_name:count)
    for corpus, chapters in tokenized.items():
        for chapter, lists_of_tokens in chapters.items():
            text_name = f"{corpus}/{chapter}"
            # print(text_name)
            for value_name, synonyms in values.items():
                cnt = sum(
                    sum(phrase.count(token_func(keyword)) for keyword in synonyms)
                    for phrase in lists_of_tokens
                )
                if not cnt:
                    continue

                occurences[(text_name, value_name)] = cnt

                if text_name not in occurences_tv:
                    occurences_tv[text_name] = {}
                assert value_name not in occurences_tv[text_name]
                occurences_tv[text_name][value_name] = cnt

                if value_name not in occurences_backref:
                    occurences_backref[value_name] = {}
                assert text_name not in occurences_backref[value_name]
                occurences_backref[value_name][text_name] = cnt

    return occurences, occurences_tv, occurences_backref


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    s = Session()

    rmdirs()
    mkdirs()
    for stem in stemmers:
        print(stem)
        tokenize_values(s, stem)
        load_source(s, stem)
