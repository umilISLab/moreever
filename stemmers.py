"""The currently supported stemmers.
To our purposes SnowballStemmer appears to be the most reasonable.
Also, notice dummy stemmer that leaves words as they are,
so algoritms can also work without stemming."""


from nltk.stem import SnowballStemmer  # type: ignore
from nltk.stem import PorterStemmer  # type: ignore
from nltk.stem import WordNetLemmatizer  # type: ignore
from nltk.stem.lancaster import LancasterStemmer  # type: ignore

# changes here need to also be reflected in static/index.html
stemmers = {
    "dummy": lambda x: x.lower(),
    "sb": SnowballStemmer("english").stem,
    # Double application of the Snowball Stemmer to ensure it is idempotent function over the values
    "sb2": lambda x: SnowballStemmer("english").stem(
        SnowballStemmer("english").stem(x)
    ),
    "ps": PorterStemmer().stem,
    "wnl": lambda x: WordNetLemmatizer().lemmatize(x.lower()),
    "lan": LancasterStemmer().stem,
}
