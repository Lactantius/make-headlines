"""Flair analysis"""

# Flair imports many modules that aren't actually needed. Faking them.
# from importlib.machinery import ModuleSpec
# class ModuleSpec:
#     """Dummy ModuleSpec class"""

#     def __init__(self, name):
#         self.name = name


# ModuleSpec(name, loader, *, origin=None, loader_state=None, is_package=None)


# def new_module(name: str, doc=None):
#     """
#     Make fake modules.
#     From https://stackoverflow.com/a/27476659/6632828
#     """
#     import sys
#     from types import ModuleType

#     m = ModuleType(name, doc)
#     m.__file__ = name + ".py"
#     m.__spec__ = ModuleSpec(name)
#     if m.__file__ != "cuda.py":
#         m.cuda = new_module("cuda")
#     m.is_available = lambda: True
#     sys.modules[name] = m
#     return m

from server.fake_module import new_module

# new_module("torch")

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
