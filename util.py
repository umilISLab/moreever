from typing import Dict, List, Optional

import os
import string
import itertools
from glob import glob
import shutil

from nltk import sent_tokenize, word_tokenize  # type: ignore
from nltk.tokenize import RegexpTokenizer  # type: ignore

from nltk.stem import WordNetLemmatizer  # type: ignore

wnl = WordNetLemmatizer()

regex_token = r"\w+"


# def clean_word(s: str) -> str:
#     return re.sub("")
def name2fname(name: str) -> str:
    return (
        name.replace(" ", "_")
        .replace("’", "_")
        .replace("'", "_")
        .replace(",", "_")
        .replace(".", "_")
        .replace("__", "_")
    )


def fname2name(fname: str) -> str:
    """_summary_

    Args:
        fname (str): _description_

    Returns:
        str: _description_
    >>> fname2name("four/Lansdowne_72-43_Transcription.html")
    'Lansdowne 72-43 Transcription'
    >>> fname2name("two/A29858_sec.html")
    'A29858 Sec'
    >>> fname2name("site/sb/variation/singles.html#Sammy")
    'Sammy'
    """
    # print(fname)
    name = (
        fname.split("/")[-1]
        .split("#")[-1]
        .replace("_s_", "'s ")
        .replace("_.", ".")
        .replace(".html", "")
        .replace(".txt", "")
    )
    assert name, f"Path {fname} is empty"
    if name.endswith("_"):
        name = name[:-1]
    name = " ".join(w[0].upper() + w[1:].lower() for w in name.split("_"))
    # print(name)
    return name

def fname2path(fname: str) -> str:
    """
    >>> fname2path("corpora/singles/Sammy.txt")
    'singles.html#sammy'
    """
    parts = fname.split("/")[-2:]
    parts[-1] = parts[-1].split(".")[0]
    name = ".html#".join(parts)
    return name.lower()

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


def rmdirs():
    from stemmers import stemmers

    for s in stemmers.keys():
        stem_dir = f"site/{s}"
        if os.path.exists(stem_dir):
            shutil.rmtree(stem_dir)


def mkdirs():
    from stemmers import stemmers
    from vocabulary import vocabulary
    from corpora import corpora

    if not os.path.exists("site"):
        os.mkdir("site")
    for s in stemmers.keys():
        nxt = f"site/{s}"
        if not os.path.exists(nxt):
            os.mkdir(nxt)
        nxt3 = f"{nxt}/values"
        if not os.path.exists(nxt3):
            os.mkdir(nxt3)

        for v in vocabulary:
            nxt4 = f"{nxt}/{v}"
            if not os.path.exists(nxt4):
                os.mkdir(nxt4)

            for c in corpora:
                nxt2 = f"{nxt4}/{c}"
                if not os.path.exists(nxt2):
                    os.mkdir(nxt2)
                nxt3 = f"{nxt2}/values"
                if not os.path.exists(nxt3):
                    os.mkdir(nxt3)


def get_dirs(path: str = "./corpora/") -> List[str]:
    result = [
        f.replace(path, "") for f in glob(f"{path}/*") if os.path.isdir(os.path.join(f))
    ]
    # TODO: remove
    assert len(set(c[0] for c in result)) == len(
        result
    ), "Each collection should start with a different letter"
    return result


def stats(fulltexts, tokenized: Dict[str, Dict[str, List[str]]]):
    symbols = {}
    texts = {}
    tokens = {}
    for c in get_dirs():
        texts[c] = len(fulltexts[c])
        symbols[c] = 0
        for tale in fulltexts[c].values():
            symbols[c] += len(tale)
        tokens[c] = 0
        for tale in tokenized[c].values():
            tokens[c] += sum(len(s) for s in tale)

    print(f"texts: {texts}")
    print(f"symbols: {symbols}")
    print(f"tokens: {tokens}")
    return texts, symbols, tokens
