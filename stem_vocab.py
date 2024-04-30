#!/bin/python
"""For a given vocabulary, classifies it according to a dictionary"""

from typing import Dict, List, Set

import csv

from stemmers import stemmers
from create import tokenize_values

tkn = "sb"
stem = stemmers[tkn]

values_src = "values-edited"
dics = []
dics += ["../dict/mfd2.0.dic"]  # Hopp
dics += ["../dict/mft_original.dic"]  # multilabel
dics += ["../dict/Provisional_dictionary.dic"]
dics += ["../dict/Refined_dictionary.dic"]  # Ponizovskiy


def classify_vocab(
    vocab_br: Dict[str, str], fname: str
) -> Dict[str, Dict[str, Set[str]]]:
    vlabels: Dict[int, str] = {}
    result: Dict[str, Dict[str, Set[str]]] = {}
    with open(fname, "r") as fin:
        for l in csv.reader(fin, delimiter="\t"):
            # print(l[0],".",l[0].strip(), ".",l[0].strip().startswith("%"),".")
            if not l or not l[0].strip() or l[0].strip().startswith("%"):
                continue
            if l[0].isdigit():
                vlabels[int(l[0])] = l[1]
                # print(f"{l[0]}\t{l[1]}")
                continue
            word = l[0].strip().lower()
            s = stem(word)
            if s not in vocab_br.keys():
                # if s.startswith("cur"):
                #     print(f".{s}.")
                #     print(vocab)
                #     print(s in vocab)
                continue
            # if one token is attributed to serveral classes, map all, even if they would be stripped later
            for ll in l[1].split(" "):
                cat = vlabels[int(ll)]
            val = vocab_br[s]
            if val in result:
                if cat in result[val]:
                    result[val][cat] = set(
                        list(result[val][cat]) + [word]
                    )  # [f"{word}({stem(word)})"])
                else:
                    result[val][cat] = {word}  # {f"{word}({stem(word)})"}
            else:
                result[val] = {}
                result[val][cat] = {word}  # {f"{word}({stem(word)})"}
    return result


if __name__ == "__main__":
    vocab, vocab_br = tokenize_values(tkn, values_src)
    # print("# Our values vocabulary:")
    # for k, v2 in vocab.items():
    #     print(f"{set(v2)}")
    # print()

    for dic in dics:
        d = dic.split("/")[1].split(".")[0]
        # the dictionary to be exported
        vs: Dict[str, List[str]] = {}
        print(f"# Dictionary: {d}")
        for k, v in classify_vocab(vocab_br, dic).items():
            # keep only stemmed tokens that belong to a single class
            if len(v) == 1:
                kv = v.popitem()
                if kv[0] in vs:
                    vs[kv[0]] += list(kv[1])
                else:
                    vs[kv[0]] = list(kv[1])
            else:
                print(f"## {k}")
                for kk, vv in v.items():
                    print(f"\t{kk}:\t{vv}")
        with open(f"{d}.values", "w") as fout:
            fout.writelines([",".join([k] + v) + "\n" for k, v in vs.items()])
        print(vs)
