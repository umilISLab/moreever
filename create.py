from typing import Dict, List, Tuple

from glob import glob

from stemmers import stemmers
from util import story_tokenize, collect_tokens, get_dirs


def tokenize_values(
    func_name: str = "sb", fname="values-edited"
) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Get the two directional dictionaries between values and labels.
    As a byproduct make a stemmed version of the values list.

    Args:
    :param str func_name: stemmer name as in stemmers.py
    :param str fname: filename without extension

    Returns:
        Tuple[Dict[str, List[str]], Dict[str, str]]: returns two dictionaries:
            value->list_labels and label->value
    """
    token_func = stemmers[func_name]
    values: Dict[str, List[str]] = {}
    valuesbackref: Dict[str, str] = {}

    with open(f"{fname}.txt") as f:
        flines = f.readlines()
        for l in flines:
            if not l.strip():
                continue
            fitems = [x.strip().lower() for x in l.split(",") if x.strip()]
            stemmed_fitems = [token_func(x) for x in fitems]
            values[stemmed_fitems[0]] = stemmed_fitems
            for i in stemmed_fitems:
                # if i in valuesbackref:
                #     print(i, stemmed_fitems[0])
                valuesbackref[i] = stemmed_fitems[0]
    with open(f"site/{func_name}/{fname}.txt", "w") as fout:
        fout.writelines("\n".join(", ".join(v) for v in values.values()))
    return values, valuesbackref


def load_source(
    token_func=None, corpora: List[str] = []
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]:
    """loads the sources from the specified directory structure

    Args:
        token_func (_type_): the used stemmer as a function. Defaults to None leads to use of dummy stemmer.
        corpora (List[str]): a list of subdirectories. Corresponds to corpora.corpora.
        Defaults to empty list, which leads to reading all subdirectories of stories/

    Returns:
        Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, List[List[str]]]]]: returns two dictionaries:
            corpora->text_name->fulltext and corpora->text_name->list of tokenized sentences
    """
    if not token_func:
        token_func = stemmers["dummy"]
    if not corpora:
        corpora = get_dirs()

    fulltexts: Dict[str, Dict[str, str]] = {}
    tokenized: Dict[str, Dict[str, List[List[str]]]] = {}
    for corpus in corpora:
        fulltexts[corpus] = {}
        tokenized[corpus] = {}
        for fname in glob(f"./stories/{corpus}/*.txt"):
            with open(fname) as f:
                talename = fname.split("/")[-1].split(".")[-2]
                fulltexts[corpus][talename] = "".join(f.readlines())
                tokenized[corpus][talename] = story_tokenize(
                    token_func, fulltexts[corpus][talename]
                )
    return fulltexts, tokenized


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
            (text_name, value): count), text_name: (value: count), value: (text_name:count),
            where text_name is in the format <corpus>/<chapter>_<text> (no extension)
    """
    token_func = stemmers[func_name]
    occurences: Dict[Tuple[str, str], int] = {}  # (text_name, value): count)
    occurences_tv: Dict[str, Dict[str, int]] = {}  # text_name: (value: count)
    occurences_backref: Dict[str, Dict[str, int]] = {}  # value: (text_name:count)
    for country, chapters in tokenized.items():
        for chapter, lists_of_tokens in chapters.items():
            text_name = f"{country}/{chapter}"
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
    for country, tales in tokenized.items():
        for tale, tokens in tales.items():
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
            tokenized[country][tale] = overall
    return tokenized


if __name__ == "__main__":
    print(tokenize_values(fname="values-flat"))
