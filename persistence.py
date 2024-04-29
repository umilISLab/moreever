from db import Session
import query

from customtypes import ClassToTokenMap, TokenizedMap

def stemmers_values():
    """values x stemmers table"""
    return query.get_stemmer2vocab(Session())

def tokenize_values(stemmer: str = "dummy"):
    return query.tokenize_values(Session(), stemmer)

def load_source(stemmer="dummy", corpora: list[str] = []):
    return query.load_source(Session(), stemmer, corpora)

def calc_occurences(values: ClassToTokenMap, tokenized: TokenizedMap):
    return query.calc_occurences(Session(), values, tokenized)

if __name__ == "__main__":
    from corpora import corpora
    stemmer = "dummy"

    values = tokenize_values(stemmer)[0]

    print(values)
    _, tokenized = load_source(stemmer, corpora)
    print(tokenized)
    _, _, occurences_backref = calc_occurences(values, tokenized)
    print(occurences_backref)
