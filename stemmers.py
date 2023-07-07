"""The currently supported stemmers.
To our purposes SnowballStemmer appears to be the most reasonable.
Also, notice dummy stemmer that leaves words as they are,
so algoritms can also work without stemming."""


from nltk.stem import SnowballStemmer
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer

stemmers = {
    "dummy": lambda x: x.lower(),
    "sb": SnowballStemmer("english").stem,
    "ps": PorterStemmer().stem,
    "wnl": lambda x: WordNetLemmatizer().lemmatize(x.lower()),
    "lan": LancasterStemmer().stem,
}
