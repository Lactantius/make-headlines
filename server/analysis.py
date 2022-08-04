"""Flair analysis"""

from flair.models import TextClassifier
from flair.data import Sentence

classifier = TextClassifier.load("sentiment")


def calc_sentiment_score(sentence: str) -> float:
    """Classify a sentence by sentiment"""

    flair_sentence = Sentence(sentence)

    # classifier.predict has not return value. Sad!
    classified_sentence = flair_sentence
    classifier.predict(classified_sentence)

    return sentence_score(classified_sentence)


def sentence_score(sentence: Sentence) -> float:
    """Extract Flair sentiment score"""

    if sentence.tag == "NEGATIVE":
        return sentence.score * -1
    else:
        return sentence.score
