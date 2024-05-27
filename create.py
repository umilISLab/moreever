"""OBSOLETE: Currently used only in auxiliary code and should be removed"""

from typing import Dict, List, Tuple

from glob import glob
import os

from settings import VOCAB, CORPORA

from stemmers import stemmers
from util import story_tokenize, collect_tokens, get_dirs, mkdirs
from flatvalues import flatten


def tokenize_values(
    func_name: str = "sb", vocab: str = ""
) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Get the two directional dictionaries between values and labels.
    As a byproduct make a stemmed version of the values list in the corresponding folder.

    Args:
    :param str func_name: stemmer name as in stemmers.py
    :param str fname: filename without path and .csv extension (.flat might be included)

    Returns:
        Tuple[Dict[str, List[str]], Dict[str, str]]: returns two dictionaries:
            value->list_labels and label->value
    """
    raise NotImplementedError("Please use equivalent method in persistence")

def load_source(
    token_func=None, corpora: List[str] = []
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]:
    """loads the sources from the specified directory structure

    Args:
        token_func (_type_): the used stemmer as a function. Defaults to None leads to use of dummy stemmer.
        corpora (List[str]): a list of subdirectories. Corresponds to corpora.corpora.
        Defaults to empty list, which leads to reading all subdirectories of corpora/

    Returns:
        Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]: returns two dictionaries:
            corpora->text_name->fulltext and corpora->text_name->list of tokenized sentences
    """
    raise NotImplementedError("Please use equivalent method in persistence")


def calc_occurences(
    values: Dict[str, List[str]],
    tokenized: Dict[str, Dict[str, List[List[str]]]],
    func_name="dummy",
) -> Tuple[
    Dict[Tuple[str, str], int], Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]
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
    raise NotImplementedError("Please use equivalent method in persistence")


def annotate_occurences(
    tokenized: Dict[str, Dict[str, List[List[str]]]],
    values_br: Dict[str, str],
    func_name="dummy",
):
    """
    Emphasises relationships between keywords and labels/values,
    by inserting a bracketed label before and after every keyword

    Args:
        tokenized (Dict[str, Dict[str, List[List[str]]]]): the tokenized text content, produced by load_source()
        values_br (Dict[str, str]): the backreference dictionary mapping labels to values, e.g. produced by tokenize_values()
        func_name (str, optional): The used stemmer, notice that stemmer is an idempotent function,
        i.e. applying it twice produces the same result. Defaults to "dummy".

    >>> tokenized = {'a':{'a':[['aa', 'bb', 'cc']]}}
    >>> values = {'bb': 'dd'}
    >>> annotate_occurences(tokenized, values)
    {'a': {'a': [['aa', 'dd', 'bb', 'dd', 'cc']]}}
    """
    token_func = stemmers[func_name]
    for corpus, texts in tokenized.items():
        for text, tokens in texts.items():
            overall = []
            for sentence in tokens:
                updated = []
                for token in sentence:
                    stemmed = token_func(token)
                    if stemmed in values_br.keys():
                        updated += [values_br[stemmed], token, values_br[stemmed]]
                    else:
                        updated += [token]
                overall += [updated]
            tokenized[corpus][text] = overall
    return tokenized


if __name__ == "__main__":
    from corpora import corpora
    from stemmers import stemmers

    stemmer = "sb"

    values, _ = tokenize_values(stemmer)
    _, tokenized = load_source(stemmers[stemmer], corpora)
    print(calc_occurences(values, tokenized, stemmer)[2])
