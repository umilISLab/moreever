from stemmers import stemmers
from corpora import corpora

from extract import get_fulltexts, corpora_tokens


def corpora_tokens_count() -> dict[str, tuple[int, int]]:
    tokens = corpora_tokens()
    result: dict[str, tuple[int, int]] = {}
    for c, texts in tokens.items():
        result[c] = (len(texts), sum(len(t) for t in texts.values()))
    # print(result)
    return result
