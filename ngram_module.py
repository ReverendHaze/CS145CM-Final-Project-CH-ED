#!/bin/python

import pickle
import os.path
import pandas as pd
import numpy as np
import time
import glob
import random

from math import log
from collections import Counter
from tweet_df import GetTweetDF
import matplotlib.pyplot as plt

from tokenizer import tokenizeRawTweetText as tokenize

OUT_FOLDER = 'out'

#Takes in raw tweet text and builds a master counter for it.
def BuildCounter(tweets, write_to_file=False):
    tprint('Failed to find counts, creating new counts pickle.')
    counter = reduce(sum, tweets.apply(BuildNGrams))

    if write_to_file:
        with open('{}/word_counts.txt'.format(OUT_FOLDER), 'w+') as f:
            strings = map(lambda x: '{}: {}\n'.format(x[0], x[1]), counter.most_common())
            f.write(''.join(strings))

        with open('{}/counter.pickle'.format(OUT_FOLDER), 'wb+') as f:
            pickle.dump(counter, f)
        tprint('    Wrote words file and counter pickle')

    return counter

#Build ngrams (and possibly our ngram counters) for a single tweet
def BuildNGrams(tweet, n=2):
    counter = Counter()
    with open('stop_words.pickle', 'rb') as f:
        stop_words = pickle.load(f)
    tokens = tokenize(tweet)
    tokens = list(filter(lambda x: x.isalpha(), tokens))
    tokens= list(filter(lambda x: x.lower() not in stop_words, tokens))
    ngram_list = []
    for i in range(len(tokens) - (n-1)):
        ngram = ' '.join(tokens[i:i+n])
        counter.update([ngram])
    return counter

def GetTopNGrams(master_df, n):
    try:
        with open('{}/counter.pickle'.format(OUT_FOLDER), 'rb') as f:
            counter = pickle.load(f)
            tprint('Loaded ngram counts from pickle.')
    except:
        BuildCounter()

    ngrams, _ = zip(*counter.most_common(n))
    return ngrams

def tprint(print_string):
    print('{}: {}'.format(time.strftime("%H:%M:%S"), print_string))

