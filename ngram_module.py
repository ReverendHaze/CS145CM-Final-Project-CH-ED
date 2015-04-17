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
def BuildCounter(tweets, write_to_file=False)
    tprint('Failed to find counts, creating new counts pickle.')
    counter = reduce(+, tweets.apply(BuildNGrams))

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



# OLD STUFF THAT MIGHT BE USEFUL FOR SENTIMENT ANALYSIS
#def build_histogram(tweets):
#    hist_list = list(map(lambda x: get_counts(x, columns), token_list))
#    return pd.DataFrame(hist_list, columns=columns).to_sparse(fill_value=0)
#
#def get_counts(tokens, columns):
#    counter = Counter(tokens)
#    return list(map(lambda x: counter[x] > 0, columns))
#fig = plt.figure()
#ax = fig.add_subplot(111)
#log_counts = list(map(log, ngram_counts[:10000]))
#ax.plot(np.arange(len(log_counts)), log_counts)
#ax.set_title('Log frequencies for top 10000 bigrams')
#fig.savefig('{}/word_frequencies.png'.format(OUT_FOLDER))

#np.arange(len(ngram_counts))
#i = 0
#if os.path.isdir('out/ngrams'):
#    os.rmdir('out/ngrams')
#os.mkdir('out/ngrams/')
#while i*WINDOW_WIDTH < num_cols:
#    tprint('Creating df for partition {}'.format(i))
#    tprint('    Building histogram...')
#    cols_df = build_histogram(twt_tokens, ngrams[i*WINDOW_WIDTH:(i+1)*WINDOW_WIDTH])
#    tprint('    Writing file...')
#    with open('out/ngrams/df{}.pickle'.format(i), 'wb+') as f:
#        pickle.dump(cols_df, f)
#    i += 1
#
#df_list = glob.glob('out/ngrams/*.pickle')
#tprint('Reading first partition')
#cols_df = pd.read_pickle('out/ngrams/df0.pickle')
#for i in np.arange(len(df_list)-1)+1:
#    tprint('Merging in partition {}'.format(i))
#    tmp_df = pd.read_pickle('out/ngrams/df{}.pickle'.format(i))
#    cols_df = pd.concat([cols_df, tmp_df]).to_sparse(fill_value=0)

