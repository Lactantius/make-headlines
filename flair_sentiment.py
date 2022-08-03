from flair.models import TextClassifier
from flair.data import Sentence

from sentiment import sentences

classifier = TextClassifier.load("sentiment")

processed_sentences = [Sentence(s) for s in sentences]


def immut_classifier(s: Sentence):
    mutated = s
    classifier.predict(mutated)
    return mutated


classifier.predict(processed_sentences)
