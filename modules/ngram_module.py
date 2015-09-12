#!/bin/python

import pickle
import os.path
import time
import glob
import random
import functools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import log
from collections import Counter

from modules.debug_module import *
from modules.tokenizer import tokenizeRawTweetText as tokenize

#Takes in raw tweet text and builds a master counter for it.
def BuildCounter(tweets, write_to_file=False):
    counter = functools.reduce(CombineCounters, map(BuildNGrams, tweets['text']), Counter())

    if write_to_file:
        with open('{}/word_counts.txt'.format(OUT_FOLDER), 'w+') as f:
            strings = map(lambda x: '{}: {}\n'.format(x[0], x[1]), counter.most_common())
            f.write(''.join(strings))

        with open('{}/counter.pickle'.format(OUT_FOLDER), 'wb+') as f:
            pickle.dump(counter, f)
        tprint('    Wrote words file and counter pickle')

    return counter

#Build ngrams (and possibly our ngram counters) for a single tweet
#Returns a counter object where the keys are bigrams and the values
#are frequency of occurrence.
def BuildNGrams(tweet, n=2):
    counter = Counter()
    with open('stop_words.pickle', 'rb') as f:
        stop_words = pickle.load(f)
    tokens = tokenize(tweet.lower())
    tokens = list(filter(lambda x: x.isalpha(), tokens))
    tokens= list(filter(lambda x: x not in stop_words, tokens))
    ngram_list = []
    for i in range(len(tokens) - (n-1)):
        ngram = ' '.join(tokens[i:i+n])
        counter.update([ngram])
    return counter

def BuildIdLists(tweets, ngrams):
    hist_list = list(map(lambda x: GetIds(x, columns), token_list))
    return pd.DataFrame(hist_list, columns=columns).to_sparse(fill_value=0)

def GetIds(tokens, columns):
    counter = Counter(tokens)
    return list(map(lambda x: counter[x] > 0, columns))

def GetTopNGrams(master_df, n):
    try:
        with open('{}/counter.pickle'.format(OUT_FOLDER), 'rb') as f:
            counter = pickle.load(f)
            tprint('Loaded ngram counts from pickle.')
    except:
        BuildCounter()

    ngrams, _ = zip(*counter.most_common(n))
    return ngrams

#Small helper function to merge two counters for the mapreduce in BuildCounter
def CombineCounters(a, b):
    a.update(b)
    return a

