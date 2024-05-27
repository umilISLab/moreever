from db import Session
import query

from customtypes import ClassToTokenMap, TokenizedMap


def stemmers_values() -> dict[str, dict[str, int]]:
    """values x stemmers table"""
    return query.get_stemmer2vocab(Session())


def tokenize_values(stemmer: str = "dummy"):
    return query.tokenize_values(Session(), stemmer)


def load_source(stemmer="dummy", corpora: list[str] = []):
    return query.load_source(Session(), stemmer, corpora)


def calc_occurences(
    stemmer: str = "dummy", flat: bool = False, aggregated: bool = False
):
    return query.calc_occurences(Session(), stemmer, flat, aggregated)


def corpora_stats() -> dict[str, tuple[int, int, int, int]]:
    """For each corpus returns: num. texts, num. words, num. sentences"""
    s = Session()
    stats = query.corpora_stats(s)
    tkns = query.corpora_token_counts(s)
    result: dict[str, tuple[int, int, int]] = {}
    for c, texts in stats.items():
        # print(texts)
        result[c] = (texts[0], texts[1], texts[2], tkns[c])
        #     len(texts),
        #     sum(t[0] for t in texts.values()),
        #     sum(t[1] for t in texts.values()),
        #     tkns[c]
        # )

    return result


if __name__ == "__main__":
    from corpora import corpora

    stemmer = "sb"

    # print(tokenize_values(stemmer))
    # print(load_source(stemmer, corpora)[1])
    print(calc_occurences(stemmer, True))
    # values = tokenize_values(stemmer)[0]

    # print(values)
    # _, tokenized = load_source(stemmer, corpora)
    # print(tokenized)
    # _, _, occurences_backref = calc_occurences(values, tokenized)
    # print(occurences_backref)
