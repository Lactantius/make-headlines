from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *

# From example at https://www.nltk.org/howto/sentiment.html
# Data downloaded for this:
# nltk.download('punkt', 'vader_lexicon', 'subjectivity')
# Supposed to user this citation:
# Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.


from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize

sentences = [
    "VADER is smart, handsome, and funny.",  # positive sentence example
    "VADER is smart, handsome, and funny!",  # punctuation emphasis handled correctly (sentiment intensity adjusted)
    "VADER is very smart, handsome, and funny.",  # booster words handled correctly (sentiment intensity adjusted)
    "VADER is VERY SMART, handsome, and FUNNY.",  # emphasis for ALLCAPS handled
    "VADER is VERY SMART, handsome, and FUNNY!!!",  # combination of signals - VADER appropriately adjusts intensity
    "VADER is VERY SMART, really handsome, and INCREDIBLY FUNNY!!!",  # booster words & punctuation make this close to ceiling for score
    "The book was good.",  # positive sentence
    "The book was kind of good.",  # qualified positive sentence is handled correctly (intensity adjusted)
    "The plot was good, but the characters are uncompelling and the dialog is not great.",  # mixed negation sentence
    "A really bad, horrible book.",  # negative sentence with booster words
    "At least it isn't a horrible book.",  # negated negative sentence with contraction
    ":) and :D",  # emoticons handled
    "",  # an empty string is correctly handled
    "Today sux",  #  negative slang handled
    "Today sux!",  #  negative slang with punctuation emphasis handled
    "Today SUX!",  #  negative slang with capitalization emphasis
    "Today kinda sux! But I'll get by, lol",  # mixed sentiment example with slang and constrastive conjunction "but"
]

paragraph = "It was one of the worst movies I've seen, despite good reviews. \
Unbelievably bad acting!! Poor direction. VERY poor production. \
The movie was bad. Very bad movie. VERY bad movie. VERY BAD movie. VERY BAD movie!"

tricky_sentences = [
    "Most automated sentiment analysis tools are shit.",
    "VADER sentiment analysis is the shit.",
    "Sentiment analysis has never been good.",
    "Sentiment analysis with VADER has never been this good.",
    "Warren Beatty has never been so entertaining.",
    "I won't say that the movie is astounding and I wouldn't claim that \
   the movie is too banal either.",
    "I like to hate Michael Bay films, but I couldn't fault this one",
    "I like to hate Michael Bay films, BUT I couldn't help but fault this one",
    "It's one thing to watch an Uwe Boll film, but another thing entirely \
   to pay for it",
    "The movie was too good",
    "This movie was actually neither that funny, nor super witty.",
    "This movie doesn't care about cleverness, wit or any other kind of \
   intelligent humor.",
    "Those who find ugly meanings in beautiful things are corrupt without \
   being charming.",
    "There are slow and repetitive parts, BUT it has just enough spice to \
   keep it interesting.",
    "The script is not fantastic, but the acting is decent and the cinematography \
   is EXCELLENT!",
    "Roger Dodger is one of the most compelling variations on this theme.",
    "Roger Dodger is one of the least compelling variations on this theme.",
    "Roger Dodger is at least compelling as a variation on the theme.",
    "they fall in love with the product",
    "but then it breaks",
    "usually around the time the 90 day warranty expires",
    "the twin towers collapsed today",
    "However, Mr. Carter solemnly argues, his client carried out the kidnapping \
   under orders and in the ''least offensive way possible.''",
]

lines_list = tokenize.sent_tokenize(paragraph)
sentences.extend(lines_list)

tricky_sentences = [
    "Most automated sentiment analysis tools are shit.",
    "VADER sentiment analysis is the shit.",
    "Sentiment analysis has never been good.",
    "Sentiment analysis with VADER has never been this good.",
    "Warren Beatty has never been so entertaining.",
    "I won't say that the movie is astounding and I wouldn't claim that \
   the movie is too banal either.",
    "I like to hate Michael Bay films, but I couldn't fault this one",
    "I like to hate Michael Bay films, BUT I couldn't help but fault this one",
    "It's one thing to watch an Uwe Boll film, but another thing entirely \
   to pay for it",
    "The movie was too good",
    "This movie was actually neither that funny, nor super witty.",
    "This movie doesn't care about cleverness, wit or any other kind of \
   intelligent humor.",
    "Those who find ugly meanings in beautiful things are corrupt without \
   being charming.",
    "There are slow and repetitive parts, BUT it has just enough spice to \
   keep it interesting.",
    "The script is not fantastic, but the acting is decent and the cinematography \
   is EXCELLENT!",
    "Roger Dodger is one of the most compelling variations on this theme.",
    "Roger Dodger is one of the least compelling variations on this theme.",
    "Roger Dodger is at least compelling as a variation on the theme.",
    "they fall in love with the product",
    "but then it breaks",
    "usually around the time the 90 day warranty expires",
    "the twin towers collapsed today",
    "However, Mr. Carter solemnly argues, his client carried out the kidnapping \
   under orders and in the ''least offensive way possible.''",
]

sentences.extend(tricky_sentences)


def print_analysis(sentences):
    for sentence in sentences:
        sid = SentimentIntensityAnalyzer()
        print(sentence)
        ss = sid.polarity_scores(sentence)
        for k in sorted(ss):
            print(f"{k}: {ss[k]}")
        print()


def vader_analysis(sentences):
    scores_list = []
    for sentence in sentences:
        sid = SentimentIntensityAnalyzer()
        ss = sid.polarity_scores(sentence)
        scores_list.append(ss)

    return scores_list


def prepare_file_analysis(filename):
    with open(filename, "r", encoding="utf-8") as f:
        sentences = []
        for line in f:
            sentences.extend(tokenize.sent_tokenize(line))
        return sentences


from numpy import mean


def averages(sentence_scores):
    sentiments = ["pos", "neg", "compound", "neu"]
    return [
        {sentiment: average_score(sentence_scores, sentiment)}
        for sentiment in sentiments
    ]


def average_score(sentence_scores: list, sentiment: str) -> float:
    return mean([score[sentiment] for score in sentence_scores])


def full_article_run(filename):
    sentences = prepare_file_analysis(filename)
    analysis = vader_analysis(sentences)
    return averages(analysis)
