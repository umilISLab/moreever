from typing import Dict, List, Optional

import os
import string
import itertools
from glob import glob

from nltk import sent_tokenize, word_tokenize  # type: ignore
from nltk.tokenize import RegexpTokenizer  # type: ignore

from nltk.stem import WordNetLemmatizer  # type: ignore

wnl = WordNetLemmatizer()

regex_token = r"\w+"


# def clean_word(s: str) -> str:
#     return re.sub("")


def fname2name(fname: str) -> str:
    """_summary_

    Args:
        fname (str): _description_

    Returns:
        str: _description_
    >>> fname2name("Germany/52_King_Thrushbeard")
    'King Thrushbeard'
    """
    #     print(fname)
    name = (
        fname.replace("_s_", "'s ")
        .replace("_.", ".")
        .replace(".html", "")
        .replace(".txt", "")
    )
    if name.endswith("_"):
        name = name[:-1]
    # TODO: should not assume <chapter>_<title> name format (see split)
    name = " ".join(w[0].upper() + w[1:].lower() for w in name.split("_")[1:])
    #     print(name)
    return name


def story_tokenize(token_func, story: str) -> List[List[str]]:
    """get the text of the story and returns a lists of sentences represented as list of lemmas.

    >>> from nltk.stem import SnowballStemmer
    >>> from nltk.stem.lancaster import LancasterStemmer
    >>> from nltk.stem import PorterStemmer
    >>> from nltk.stem import WordNetLemmatizer
    >>> wnl = WordNetLemmatizer().lemmatize
    >>> ps = PorterStemmer().stem
    >>> sb = SnowballStemmer("english").stem
    >>> lan = LancasterStemmer().stem
    >>> story = "Once upon a time in the forest. Then something else happened! There's also open-mindedness. And so the story ends."
    >>> story_tokenize(lambda x: x, story)
    [['once', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'something', 'else', 'happened'], ['there', 's', 'also', 'open', 'mindedness'], ['and', 'so', 'the', 'story', 'ends']]
    >>> story_tokenize(wnl, story)
    [['once', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'something', 'else', 'happened'], ['there', 's', 'also', 'open', 'mindedness'], ['and', 'so', 'the', 'story', 'end']]
    >>> story_tokenize(ps, story)
    [['onc', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'someth', 'els', 'happen'], ['there', 's', 'also', 'open', 'minded'], ['and', 'so', 'the', 'stori', 'end']]
    >>> story_tokenize(sb, story)
    [['onc', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'someth', 'els', 'happen'], ['there', 's', 'also', 'open', 'minded'], ['and', 'so', 'the', 'stori', 'end']]
    >>> story_tokenize(lan, story)
    [['ont', 'upon', 'a', 'tim', 'in', 'the', 'forest'], ['then', 'someth', 'els', 'hap'], ['ther', 's', 'also', 'op', 'mind'], ['and', 'so', 'the', 'story', 'end']]
    >>> story = "marriage married"
    >>> story_tokenize(wnl, story)
    [['marriage', 'married']]
    >>> story_tokenize(ps, story)
    [['marriag', 'marri']]
    >>> story_tokenize(sb, story)
    [['marriag', 'marri']]
    >>> story_tokenize(lan, story)
    [['marry', 'marry']]
    """
    tokens = []
    tokenizer = RegexpTokenizer(regex_token)

    sentences = sent_tokenize(story)
    for i, sentence in enumerate(sentences):
        # doc = word_tokenize(sentence)
        doc = tokenizer.tokenize(sentence)
        tokens += [
            [token_func(t.lower()) for t in doc if t not in string.punctuation + "\n"]
        ]
    return tokens


def collect_tokens(
    tokenized: Dict[str, Dict[str, List[List[str]]]],
    corpus: Optional[str] = None,
) -> List[List[str]]:
    """
    >>> data = {'A': {'1': [['aa', 'bb'], ['cc']], '2':[['c', 'd']]}, 'B': {'I': [['a', 'b']], 'II': [['bd', 'ce', 'cf'], ['ff']]}}
    >>> collect_tokens(data, 'A')
    [['aa', 'bb'], ['cc'], ['c', 'd']]

    >>> collect_tokens(data, 'B')
    [['a', 'b'], ['bd', 'ce', 'cf'], ['ff']]

    >>> collect_tokens(data)
    [['aa', 'bb'], ['cc'], ['c', 'd'], ['a', 'b'], ['bd', 'ce', 'cf'], ['ff']]


    """
    result = []
    if corpus:
        # result = list(tokenized[corpus].values())
        result = list(itertools.chain(*list(tokenized[corpus].values())))
    else:
        for c in tokenized.keys():
            result += collect_tokens(tokenized, c)
    return result


def get_dirs(path: str = "./stories/"):
    result = [
        f.replace(path, "") for f in glob(f"{path}/*") if os.path.isdir(os.path.join(f))
    ]
    assert len(set(c[0] for c in result)) == len(result)
    return result


def stats(fulltexts, tokenized: Dict[str, Dict[str, List[str]]]):
    symbols = {}
    tales = {}
    tokens = {}
    for c in get_dirs():
        tales[c] = len(fulltexts[c[0]])
        symbols[c] = 0
        for tale in fulltexts[c[0]].values():
            symbols[c] += len(tale)
        tokens[c] = 0
        for tale in tokenized[c[0]].values():
            tokens[c] += sum(len(s) for s in tale)

    print(f"tales: {tales}")
    print(f"symbols: {symbols}")
    print(f"tokens: {tokens}")
    return tales, symbols, tokens
