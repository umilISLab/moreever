from stemmers import stemmers
from corpora import corpora

from persistence import corpora_token_counts


def corpora_tokens_count() -> dict[str, tuple[int, int, int]]:
    """For each corpus returns: num. texts, num. words, num. sentences"""
    tokens = corpora_token_counts()
    result: dict[str, tuple[int, int, int]] = {}
    for c, texts in tokens.items():
        result[c] = (
            len(texts),
            sum(t[0] for t in texts.values()),
            sum(t[1] for t in texts.values()),
        )
    # print(result)
    return result
