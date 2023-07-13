from gensim.models import Word2Vec  # type: ignore
from gensim.models import FastText  # type: ignore

"""
class GloVe:
    corpus_count
    wv
    def __init__(self, sentences, vector_size, window, min_count, workers, epochs):
        self.corpus_count = sum(len(s) for s in sentences)
    
    def train(self, sentences, epochs, total_examples):
        pass
    
    def save(self, fname):
        
    # https://stackoverflow.com/a/15774013/1827854
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result    
"""
algos = {
    "model": Word2Vec,
    "w2v": Word2Vec,
    "w2v2": Word2Vec,
    "w2v3": Word2Vec,
    "w2v4": Word2Vec,
    "fasttext": FastText,
    "ft": FastText,
    "ft2": FastText,
    "ft3": FastText,
    "ft4": FastText,
}

reverse_algos = {}
for k, v in algos.items():
    if v.__name__ not in reverse_algos:
        reverse_algos[v.__name__] = [k]
    else:
        reverse_algos[v.__name__] += [k]

algo = "fasttext"
# algo = "w2v"
# model_dir = "/media/data/models"

epochs = 200
