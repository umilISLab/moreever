"""The currently supported stemmers.
To our purposes SnowballStemmer appears to be the most reasonable.
Also, notice dummy stemmer that leaves words as they are,
so algoritms can also work without stemming."""

import nltk  # type: ignore
import simplemma
import spacy

from settings import lang

from morphroot import get_root_morpheme, roots

# nltk.download("wordnet")
nlp = spacy.load(f"{lang}_core_web_lg")

# changes here need to also be reflected in static/index.html
# en
all_stemmers = {
    "en": {
        "dummy": lambda word, sent: word.lower(),
        "wnl": lambda word, sent: nltk.stem.WordNetLemmatizer().lemmatize(word.lower()),
        "sb": lambda word, sent: nltk.stem.SnowballStemmer("english").stem(word.lower()),
        # Double application of the Snowball Stemmer to ensure it is idempotent function over the values
        "sb2": lambda word, sent: nltk.stem.SnowballStemmer("english").stem(
            nltk.stem.SnowballStemmer("english").stem(word.lower())
        ),
        # Snowball stemmer on lemmatized tokens
        "sb-lem": lambda word, sent: nltk.stem.SnowballStemmer("english").stem(
            nltk.stem.WordNetLemmatizer().lemmatize(word.lower())
        ),
        "ps": lambda word, sent: nltk.stem.PorterStemmer().stem(word.lower()),
        "lan": lambda word, sent: nltk.stem.lancaster.LancasterStemmer().stem(word.lower()),
        # "morph": lambda x: get_root_morpheme(nltk.stem.WordNetLemmatizer().lemmatize(x.lower()), roots),
    },
    "it": {
        "dummy": lambda word, sent: word.lower(),
        "simpl": lambda word, sent: simplemma.lemmatize(word.lower(), lang="it"),
        "sb": lambda word, sent: nltk.stem.SnowballStemmer("italian").stem(word.lower()),
        # Double application of the Snowball Stemmer to ensure it is idempotent function over the values
        "sb2": lambda word, sent: nltk.stem.SnowballStemmer("italian").stem(
            nltk.stem.SnowballStemmer("italian").stem(word.lower())
        ),
    },
}


stemmers = all_stemmers[lang]

stemmer_labels = {
    "dummy": "none (exact words)",
    "sb": "SnowBall Stemmer",
    "sb2": "SnowBall repeated",
    "ps": "Porter Stemmer",
    "lan": "Lancaster Stemmer",
    "morph": "Morphological Root",
    "sb-lem": "Stemmed Lemmas",
    "wnl": "Lemmatizer",
    "simpl": "Lemmatizer",
}
