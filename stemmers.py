"""The currently supported stemmers.
To our purposes SnowballStemmer appears to be the most reasonable.
Also, notice dummy stemmer that leaves words as they are,
so algoritms can also work without stemming."""

import nltk  # type: ignore
import simplemma

# from morphroot import get_root_morpheme

nltk.download("wordnet")

# changes here need to also be reflected in static/index.html
# en
stemmers = {
    "dummy": lambda x: x.lower(),
    "wnl": lambda x: nltk.stem.WordNetLemmatizer().lemmatize(x.lower()),
    "sb": nltk.stem.SnowballStemmer("english").stem,
    # Double application of the Snowball Stemmer to ensure it is idempotent function over the values
    "sb2": lambda x: nltk.stem.SnowballStemmer("english").stem(
        nltk.stem.SnowballStemmer("english").stem(x)
    ),
    "ps": nltk.stem.PorterStemmer().stem,
    "lan": nltk.stem.lancaster.LancasterStemmer().stem,
    # "morph": get_root_morpheme,
}


# it
stemmers = {
    "dummy": lambda x: x.lower(),
    "simpl": lambda x: simplemma.lemmatize(x, lang='it'),
    "sb": nltk.stem.SnowballStemmer("italian").stem,
    # Double application of the Snowball Stemmer to ensure it is idempotent function over the values
    "sb2": lambda x: nltk.stem.SnowballStemmer("italian").stem(
        nltk.stem.SnowballStemmer("italian").stem(x)
    ),
}

stemmer_labels = {
    "dummy": "none",
    "sb": "SnowBall Stemmer",
    "sb2": "SnowBall repeated",
    "ps": "Porter Stemmer",
    "lan": "Lancaster Stemmer",
    "wnl": "Lemmatizer",
    "simpl": "Lemmatizer",
}

