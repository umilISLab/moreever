"""The currently supported stemmers.
To our purposes SnowballStemmer appears to be the most reasonable.
Also, notice dummy stemmer that leaves words as they are,
so algoritms can also work without stemming."""

import nltk  # type: ignore
from morphroot import get_root_morpheme

nltk.download("wordnet")
# changes here need to also be reflected in static/index.html
stemmers = {
    "dummy": lambda x: x.lower(),
    "sb": nltk.stem.SnowballStemmer("english").stem,
    # Double application of the Snowball Stemmer to ensure it is idempotent function over the values
    "sb2": lambda x: nltk.stem.SnowballStemmer("english").stem(
        nltk.stem.SnowballStemmer("english").stem(x)
    ),
    "ps": nltk.stem.PorterStemmer().stem,
    "wnl": lambda x: nltk.stem.WordNetLemmatizer().lemmatize(x.lower()),
    "lan": nltk.stem.lancaster.LancasterStemmer().stem,
    "morph": get_root_morpheme,
}
