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
