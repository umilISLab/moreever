"""The main class that enables annotation of the full-text while processing a stemmed version of it.
"""

from re import fullmatch
from typing import Dict, List, Union

import nltk  # type: ignore

from stemmers import stemmers
from create import tokenize_values

regex_token = r"\w+"
language = "english"

from template import span_templ

nltk.download("punkt")


class Annotator:
    def __init__(self, tokenizer_name, fulltext: str, values_br: Dict[str, str] = {}):
        self.token_func = stemmers[tokenizer_name]
        self.func_name = tokenizer_name
        # label->value dict
        self.values = values_br if values_br else tokenize_values(tokenizer_name)[1]
        self.fulltext = fulltext
        self.tokenizer = nltk.tokenize.RegexpTokenizer(regex_token)
        self.sent_tokenizer = nltk.data.load(f"tokenizers/punkt/{language}.pickle")

    def rich_text(self):
        """
        >>> from nltk.stem.lancaster import LancasterStemmer
        >>> lan = LancasterStemmer().stem
        >>> s = "Once upon a time in the forest. Then there was a wedding and devotion! There's also open-mindedness and fairness. And so the story ends."
        >>> Annotator('lan', s).rich_text()
        "Once upon a time in the forest. Then there was a <span id='lov-0' class='wed lov' title='wedding'>wedding</span> and <span id='loy-0' class='devot loy' title='devotion'>devotion</span>! There's also open-mindedness and <span id='just-0' class='fair just' title='fairness'>fairness</span>. And so the story ends."
        >>> s = "There was once a man whose wife died, and a woman whose husband died, and thend a woman whose husband died, and the man had a daughter, and the woman also had a daughter."
        >>> Annotator('lan', s).rich_text()
        "There was once a man whose <span id='lov-0' class='wif lov' title='wife'>wife</span> died, and a woman whose <span id='lov-0' class='husband lov' title='husband'>husband</span> died, and thend a woman whose <span id='lov-0' class='husband lov' title='husband'>husband</span> died, and the man had a daughter, and the woman also had a daughter."
        >>> s = "Three women were changed into flowers which grew in the field, but one of them was allowed to be in her own home at night. Then once when day was drawing near, and she was forced to go back to her companions in the field and become a flower again, she said to her husband, “If thou wilt come this afternoon and gather me, I shall be set free and henceforth stay with thee.” And he did so. Now the question is, how did her husband know her, for the flowers were exactly alike, and without any difference? Answer: as she was at her home during the night and not in the field, no dew fell on her as it did on the others, and by this her husband knew her."
        >>> Annotator('lan', s).rich_text()
        "Three women were changed into flowers which grew in the field, but one of them was allowed to be in her own home at night. Then once when day was drawing near, and she was forced to go back to her companions in the field and become a flower again, she said to her <span id='lov-0' class='husband lov' title='husband'>husband</span>, “If thou wilt come this afternoon and gather me, I shall be set <span id='fre-0' class='fre fre' title='free'>free</span> and henceforth stay with thee.” And he did so. Now the question is, how did her <span id='lov-0' class='husband lov' title='husband'>husband</span> <span id='know-0' class='know know' title='know'>know</span> her, for the flowers were exactly alike, and without any difference? Answer: as she was at her home during the night and not in the field, no dew fell on her as it did on the others, and by this her <span id='lov-0' class='husband lov' title='husband'>husband</span> knew her."
        """
        values_count = {v: 0 for v in set(self.values.values())}
        # print(len(tokens), tokens)
        result = []
        for paragraph in self.fulltext.split("\n"):
            # print(paragraph)
            tokens = self.tokens(paragraph)
            sentences = self.sent_tokenizer.tokenize(paragraph)
            # print(sentences)
            sent_spans = list(self.sent_tokenizer.span_tokenize(paragraph))
            # print(sent_spans)
            annotated_text = paragraph
            for i, sentence in reversed(list(enumerate(sentences))):
                ranges = list(self.tokenizer.span_tokenize(sentence))
                doc = self.tokenizer.tokenize(sentence)
                annotated_sentence = sentence
                for j, t in reversed(list(enumerate(doc))):
                    if tokens[i][j] in self.values.keys():
                        value = self.values[tokens[i][j]]
                        sid = f"{value}-{values_count[value]}"
                        stype = f"{tokens[i][j]} {value}"
                        title = value
                        # title = annotated_sentence[ranges[j][0] : ranges[j][1]]
                        annotated_sentence = (
                            annotated_sentence[: ranges[j][0]]
                            + span_templ.format(
                                id=sid,
                                type=stype,
                                title=title,
                                content=t,
                            )
                            + annotated_sentence[ranges[j][1] :]
                        )
                annotated_text = (
                    annotated_text[: sent_spans[i][0]]
                    + annotated_sentence
                    + annotated_text[sent_spans[i][1] :]
                )
            # print(annotated_text)
            # if annotated_text:
            result += [annotated_text]

        result = "\n".join(result)
        result = result.replace("\n\n\n", "\n\n")
        result = result.replace("\n\n", "</p><p>")
        result = result.replace("\n", "<br/>")
        result = f"<p>{result}</p>"
        # return "<p>" + "</p><p>".join(result) + "</p>"
        return result

    def tokens(self, fulltext) -> List[List[str]]:
        """get the text of the story and returns a list of lemmas
        >>> from nltk.stem import SnowballStemmer
        >>> from nltk.stem.lancaster import LancasterStemmer
        >>> from nltk.stem import PorterStemmer
        >>> from nltk.stem import WordNetLemmatizer
        >>> wnl = WordNetLemmatizer().lemmatize
        >>> ps = PorterStemmer().stem
        >>> sb = SnowballStemmer("english").stem
        >>> lan = LancasterStemmer().stem
        >>> s = "Once upon a time in the forest. Then something else happened! There's also open-mindedness. And so the story ends."
        >>> Annotator('dummy', s).tokens()
        [['once', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'something', 'else', 'happened'], ['there', 's', 'also', 'open', 'mindedness'], ['and', 'so', 'the', 'story', 'ends']]
        >>> Annotator('wnl', s).tokens()
        [['once', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'something', 'else', 'happened'], ['there', 's', 'also', 'open', 'mindedness'], ['and', 'so', 'the', 'story', 'end']]
        >>> Annotator('ps', s).tokens()
        [['onc', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'someth', 'els', 'happen'], ['there', 's', 'also', 'open', 'minded'], ['and', 'so', 'the', 'stori', 'end']]
        >>> Annotator('sb', s).tokens()
        [['onc', 'upon', 'a', 'time', 'in', 'the', 'forest'], ['then', 'someth', 'els', 'happen'], ['there', 's', 'also', 'open', 'minded'], ['and', 'so', 'the', 'stori', 'end']]
        >>> Annotator('lan', s).tokens()
        [['ont', 'upon', 'a', 'tim', 'in', 'the', 'forest'], ['then', 'someth', 'els', 'hap'], ['ther', 's', 'also', 'op', 'mind'], ['and', 'so', 'the', 'story', 'end']]
        >>> s = "marriage married"
        >>> Annotator('wnl', s).tokens()
        [['marriage', 'married']]
        >>> Annotator('ps', s).tokens()
        [['marriag', 'marri']]
        >>> Annotator('sb', s).tokens()
        [['marriag', 'marri']]
        >>> Annotator('lan', s).tokens()
        [['marry', 'marry']]
        """
        tokens = []
        sentences = self.sent_tokenizer.tokenize(fulltext)
        for sentence in sentences:
            doc = self.tokenizer.tokenize(sentence)
            tokens += [
                [
                    self.token_func(t.lower()) for t in doc
                ]  # if t not in string.punctuation + "\n"]
            ]
        return tokens
