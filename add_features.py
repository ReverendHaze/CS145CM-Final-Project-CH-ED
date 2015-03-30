#!/bin/python

import pickle
import os.path
import pandas as pd
import numpy as np
from math import log
from collections import Counter
from pickle_to_df import CreateDF
from multiprocessing import Pool
import matplotlib.pyplot as plt

from tokenizer import tokenizeRawTweetText as tokenize

#Update our ngram counters with a new tweet
def update_ngrams(g_counter, tweet, token_filter=None, n=2):
    tokens = tokenize(tweet.text)
    if token_filter is not None:
        tokens = list(filter(lambda x: x in token_filter, tokens))
    ngrams = len(tokens)-(n-1)
    for i in range(ngrams):
        g_counter.update([' '.join(tokens[i:i+n])])
    return tokens

def build_histogram(token_list, columns):
    hist_list = list(map(lambda x: get_counts(x, columns), token_list))
    return pd.DataFrame(hist_list, columns=columns)

def get_counts(tokens, columns):
    counter = Counter(tokens)
    return list(map(lambda x: counter[x], columns))

OUT_FOLDER = 'out'

out_filename = '{}/master.pickle'.format(OUT_FOLDER)
try:
    with open(out_filename, 'rb') as f:
        master_df = pickle.load(f)
except:
    print('Failed to open master pickle file, creating now.')
    CreateDF(out_filename)
    with open(out_filename, 'rb') as f:
        master_df = pickle.load(f)

master_df = master_df.head(1000)

counter = Counter()
twt_tokens = master_df.apply(lambda x: update_ngrams(counter, x), axis=1)

with open('word_counts.txt', 'w+') as f:
    strings = map(lambda x: '{}: {}\n'.format(x[0], x[1]), counter.most_common())
    f.write(''.join(strings))

ngrams, _ = zip(*counter.most_common(40000))
cols_df = build_histogram(twt_tokens, ngrams)
join_index = np.arange(cols_df.shape[0])
master_df['join'] = join_index
cols_df['join'] = join_index
master_df = master_df.join(cols_df, on='join')

