from typing import Dict, Iterable, List, Set, Tuple

import itertools

import networkx as nx  # type: ignore
from networkx.algorithms import community  # type: ignore

from settings import model_dir

from stemmers import stemmers
from corpora import corpora
from algo import algos
from template import venn_templ

from create import tokenize_values, load_source, calc_occurences


def render_venn(ckeywords: List[str], title: str = "") -> str:
    keywords = [ckeywords[c] for c in corpora]

    word_cls = {
        "a_b_c": keywords[0] & keywords[1] & keywords[2],
        "a": keywords[0] - keywords[1] - keywords[2],
        "b": keywords[1] - keywords[0] - keywords[2],
        "c": keywords[2] - keywords[0] - keywords[1],
    }
    word_cls["a_b"] = (keywords[0] & keywords[1]) - word_cls["a_b_c"]
    word_cls["a_c"] = (keywords[0] & keywords[2]) - word_cls["a_b_c"]
    word_cls["b_c"] = (keywords[1] & keywords[2]) - word_cls["a_b_c"]

    tag_cls = {
        k: "".join(
            [
                f'<tspan x="0" y="{i*11}" font-size="smaller">{p}</tspan>'
                for i, p in enumerate(sorted(list(word_cls[k])))
            ]
        )
        for k, v in word_cls.items()
    }

    tag_cls["a_name"] = corpora[0]
    tag_cls["b_name"] = corpora[1]
    tag_cls["c_name"] = corpora[2]
    tag_cls["title"] = title

    return venn_templ.format(**tag_cls)

def keywords_venn(
    tkn: str,
    vocab: str = "",
    values: Dict[str, List[str]] = {},
    tokenized: Dict[str, Dict[str, List[List[str]]]] = {},
    occurences_tv: Dict[str, Dict[str, int]] = {},
) -> str:
    """_summary_

    Args:
        tkn (str): stemmer name, see semmers
        fname (str, optional): need to provide either fname or other parameters.
        values (Dict[str, List[str]], optional): see create.tokenize_values(). Recalculated when missing.
        tokenized (Dict[str, Dict[str, List[List[str]]]], optional): see create.load_source(). Recalculated when missing.
        occurences_tv (Dict[str, Dict[str, int]], optional): see create.calc_occurences(). Recalculated when missing.
    """
    if not values or not tokenized or not occurences_tv:
        values, _ = tokenize_values(tkn, vocab=vocab)
        _, tokenized = load_source(stemmers[tkn], corpora)
        _, occurences_tv, _ = calc_occurences(values, tokenized)

    ckeywords: Dict[str, Set[str]] = {}
    for c in corpora:
        ckeywords[c] = set(
            itertools.chain(
                *[list(v.keys()) for k, v in occurences_tv.items() if k.startswith(c)]
            )
        )
    return render_venn(ckeywords, "Venn Diagram of Labels in Corpora")


def clusters(
    tkn: str,
    algo: str = "w2v",
    fname: str = "",
    epochs: int = 200,
    threshold=0.13,
    iteration: int = 0,
    values: Dict[str, List[str]] = {},
    occurences_tv: Dict[str, Dict[str, int]] = {},
) -> Dict[str, Set[Tuple[str, ...]]]:
    """_summary_

    Args:
        tkn (str): _description_
        algo (str, optional): _description_. Defaults to "w2v".
        fname (str, optional): _description_. Defaults to "".
        epochs (int, optional): _description_. Defaults to 200.
        threshold (float, optional): _description_. Defaults to 0.13.
        iteration (int, optional): _description_. Defaults to 0.
        values (Dict[str, List[str]], optional): _description_. Defaults to {}.
        tokenized (Dict[str, Dict[str, List[List[str]]]], optional): _description_. Defaults to {}.
        occurences_tv (Dict[str, Dict[str, int]], optional): _description_. Defaults to {}.

    Returns:
        Dict[str, List[List[str]]]: corpus -> list of clusters
    """
    try:
        models = {
            c: algos[algo].load(f"{model_dir}/{c}.{tkn}.e{epochs}.{algo}.{iteration}")
            for c in corpora
        }
    except FileNotFoundError as fnfe:
        print(fnfe)
        return {}
    keywords = sorted(list(values.keys()))

    ckeywords = {}
    for c in corpora:
        kws = set(
            itertools.chain(
                *[
                    list(v.keys())
                    for k, v in occurences_tv.items()
                    if k.startswith(c[0])
                ]
            )
        )
        ckeywords[c] = sorted(list(kws))

    # keywords = sorted(list(set(occurences_backref.keys())))
    G = {c: nx.Graph() for c in corpora}
    for c, m in models.items():
        for i, k in enumerate(keywords):
            for x in keywords[i + 1 :]:
                if k not in ckeywords[c] or x not in ckeywords[c]:
                    continue
                try:
                    sim = m.wv.similarity(k, x)
                    if sim >= threshold:
                        G[c].add_edge(k, x, weight=float(sim))
                except KeyError:
                    pass

    clusters: Dict[str, Set[Tuple[str, ...]]] = {}
    for corpus, g in G.items():
        # Clique percolation with k=2 is just clustered by the edges
        cliques = community.k_clique_communities(g, k=2)
        # print(list(cliques))
        # clusters[country] = list[cliques]
        # clusters[country] = [c for c in cliques]
        # clusters[country] = [[c for c in clique] for clique in community.k_clique_communities(g, k=2)]
        clusters[corpus] = set(
            [
                tuple([c for c in clique])
                # [c for c in clique]
                for clique in community.k_clique_communities(g, k=2)
            ]
        )
        # print(clusters[country])
        # print("CLUSTER {}".format(i))

    return clusters


def filter_clusters_containing(
    clusters: Set[Tuple[str, ...]], word: str
) -> Set[Tuple[str, ...]]:
    # print(clusters)
    return set(cl for cl in clusters if word in list(cl))


def clusters_venn(
    tkn: str = "sb",
    algo: str = "w2v",
    vocab: str = "values-edited",
    epochs: int = 200,
    threshold=0.13,
    iteration: int = 7,
    values: Dict[str, List[str]] = {},
    occurences_tv: Dict[str, Dict[str, int]] = {},
) -> Dict[str, str]:
    if not values or not occurences_tv:
        values, _ = tokenize_values(tkn, vocab)
        _, tokenized = load_source(stemmers[tkn], corpora)
        _, occurences_tv, _ = calc_occurences(values, tokenized)

    cl = clusters(tkn, algo, vocab, epochs, threshold, iteration, values, occurences_tv)
    # print(cl)
    result: Dict[str, str] = {}
    if len(cl) != 3:
        print(
            f"Skipping: clusters for {model_dir}/*.{tkn}.e{epochs}.{algo}.{iteration}."
            "Consider creating the corresponding model with createmodel.py."
        )
        return {}
    for v in values:
        per_corpus = {c: filter_clusters_containing(cl[c], v) for c in corpora}
        # if exactly one cluster per corpus contains the value
        if len([k for k, v in per_corpus.items() if len(v) == 1]) == 3:
            print(per_corpus)
            result[v] = render_venn({k: set(v.pop()) for k, v in per_corpus.items()})
    return result


if __name__ == "__main__":
    clusters_venn()
