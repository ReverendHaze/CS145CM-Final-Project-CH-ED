#!/bin/python

import pickle
import os.path
import pandas as pd
import numpy as np
import time
import glob

from math import log
from collections import Counter
from pickle_to_df import CreateDF
import matplotlib.pyplot as plt

from tokenizer import tokenizeRawTweetText as tokenize

OUT_FOLDER = 'out'
PARTITIONS = 20

def CreateNGramDF(master_df):

def tprint(print_string):
    print('{}: {}'.format(time.strftime("%H:%M:%S"), print_string))

#Build ngrams (and possibly our ngram counters) for a new tweet
def BuildNGrams(tweet, stop_words, g_counter=None, n=2):
    tokens = tokenize(tweet)
    tokens= list(filter(lambda x: x not in stop_words, tokens))
    tokens = list(filter(lambda x: not isalpha(), tokens))
    ngram_list = []
    for word in range(len(tokens) - (n-1)):
        ngram = ' '.join(tokens[i:i+n])
        ngram_list.append(ngram)
        if g_counter is not None:
            g_counter.update([ngram])
    return ngram_list

def build_histogram(token_list, columns):
    hist_list = list(map(lambda x: get_counts(x, columns), token_list))
    return pd.DataFrame(hist_list, columns=columns).to_sparse(fill_value=0)

def get_counts(tokens, columns):
    counter = Counter(tokens)
    return list(map(lambda x: counter[x] > 0, columns))

out_filename = '{}/master.pickle'.format(OUT_FOLDER)
try:
    with open(out_filename, 'rb') as f:
        master_df = pickle.load(f)
        master_df = master_df[['id', 'text']]
        num_tweets = len(master_df.index)
        master_df = master_df.head(100000)
        tprint('Loaded master pickle, total of {} tweets'.format(num_tweets))
except:
    tprint('Failed to open master pickle file, creating now.')
    CreateDF(out_filename)
    with open(out_filename, 'rb') as f:
        master_df = pickle.load(f)
    tprint('    Wrote new master pickle.')
try:
    with open('{}/counter.pickle'.format(OUT_FOLDER), 'rb') as f:
        counter = pickle.load(f)
        tprint('Loaded ngram counts from pickle')
        with open('stop_words.pickle', 'rb') as f:
            stop_words = pickle.load(f)
        twt_tokens = master_df['text'].apply(lambda x: build_ngrams(x, stop_words))
except:
    tprint('Failed to find counts, creating new counts pickle.')
    counter = Counter()
    tprint('    Generating ngrams')
    twt_tokens = master_df['text'].apply(lambda x: build_ngrams(x, g_counter=counter))
    tprint('    Finished ngram generation')

    with open('{}/word_counts.txt'.format(OUT_FOLDER), 'w+') as f:
        strings = map(lambda x: '{}: {}\n'.format(x[0], x[1]), counter.most_common())
        f.write(''.join(strings))

    with open('{}/counter.pickle'.format(OUT_FOLDER), 'wb+') as f:
        pickle.dump(counter, f)

    tprint('    Wrote words file and counter pickle')

#Reduce memory usage since the following steps are very resource intensive
ids = master_df['id']
master_df = 0

tprint('Building dataframe with common bigrams')
ngrams, ngram_counts = zip(*counter.most_common())
num_cols = 10000
counter = 0

window = num_cols // PARTITIONS

fig = plt.figure()
ax = fig.add_subplot(111)
log_counts = list(map(math.log, ngram_counts[:10000]))
ax.plot(np.arange(len(ngram_counts)), ngram_counts)
ax.title('Log frequencies for top 10000 bigrams')
fig.savefig('{}/word_frequencies.png')

np.arange(len(ngram_counts))
i = 0
os.mkdir('/tmp/ngrams/')
while i*window < num_cols:
    tprint('Creating df for partition {}'.format(i))
    cols_df = build_histogram(twt_tokens[i*window:(i+1)*window], ngrams)
    with open('/tmp/ngrams/df{}.pickle'.format(i), 'wb+') as f:
        pickle.dump(cols_df, f)
    i += 1

#df_list = glob.glob('/tmp/ngrams/*.pickle')
#tprint('Reading first partition')
#cols_df = pd.read_pickle('/tmp/ngrams/df0.pickle')
#for i in np.arange(PARTITIONS-1)+1:
#    tprint('Merging in partition {}'.format(i))
#    tmp_df = pd.read_pickle('/tmp/ngrams/df{}.pickle'.format(i))
#    cols_df = pd.concat([cols_df, tmp_df]).to_sparse(fill_value=0)
#
#cols_df['id'] = ids.to_sparse(fill_value=0)
#tprint('Finished creating bigram dataframe.')
#
#with open('{}/bigrams.pickle', 'wb+') as f:
#    pickle.dump(cols_df, f)
if __name__ == '__main__':

