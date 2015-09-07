#!/bin/python

# Prepackaged modules
import pickle
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from operator import itemgetter

# Our modules
import tweet_df as tweet_df
import modules.graph_module as graph_module
import modules.cluster_module as cluster_module
import modules.ngram_module as ngram_module
import modules.burst_module as burst_module
import modules.dimension_module as dim_module
from modules.debug_module import *

SAMPLE_SIZE = 1000000

# Code to execute when the script is run
def main():

    # Build the dataframes for all tweets, creating
    # them from the data files if necessary and building
    # incrementally with new files.
    tweet_df.MakeTweetDF()
    #
    # define dictionaries for bursty tweet lists and zscore dfs
    for city in 'Chicago', 'Houston', 'LA':
        hist_filename = 'out/hist/{}_hist.pickle'.format(city)
        try:
            with open(hist_filename, 'rb') as f:
                hist_df = pickle.load(f)
        except:
            master_df = tweet_df.GetCity(city)
            master_df = master_df.dropna(axis=0, how='any', subset=['id', 'text', 'created_at'])
            master_df = master_df[(master_df['created_at'] != 'None')]
            tprint('Tweets for {}: {}'.format(city, len(master_df.index)))
            if len(master_df.index.values) > SAMPLE_SIZE:
                sample_ids = np.random.choice(master_df.index.values, SAMPLE_SIZE)
                master_df = master_df.ix[sample_ids]
                tprint('Cut down to {} tweets'.format(SAMPLE_SIZE))

            master_df.index = master_df.apply(lambda x: datetime.datetime.strptime(x.created_at, "%a %b %d %H:%M:%S %z %Y"), axis=1)
            master_df = master_df[master_df['created_at'].notnull()]
            del master_df['created_at']

            # Graph tweet rate over time
            graph_module.GraphFreqs(master_df, city=city)

            # Graph the number of tweets within each part of each city
            graph_module.GraphHexBin(master_df, city)

            #Graph clusters with KMeans and Spectral Clustering
            #tprint('Generating and graphing kmeans clusters')
            #cluster_module.GetClusters(master_df, city, n_clusters=12, how='kmeans')
            #tprint('Generating and graphing spectral clusters')
            #cluster_module.GetClusters(master_df, city, n_clusters=12, how='spectral')

            #Temporal histogram calculation
            hist_df = burst_module.Histogram(master_df, city)
            with open(hist_filename, 'wb+') as f:
                pickle.dump(hist_df, f)
        tprint('Finished building histograms, saving file...')
        tprint('Converting to matrix')
        hist_mat = hist_df.as_matrix()
        tprint('Finding matrix rank')
        hist_rank = np.linalg.matrix_rank(hist_mat)
        tprint('Current matrix dimensions: {}'.format(hist_mat.shape))
        tprint('Pre-reduction matrix rank: {}'.format(hist_rank))

        approx_rank = 100
        # dimensionality reduction
        tprint('Starting Sparse NMF')
        filename = 'out/NMF_{}_{}.pickle'.format(city, approx_rank)
        tprint('hist_mat shape pre-reduction: {}'.format(hist_mat.shape))
        model = dim_module.GetTrainedModel(hist_mat.transpose(), approx_rank, 'NMF')
        topics = dim_module.GetTopics(model, 4, hist_df.index.values)
        topics = sorted([ topics[key] for key in topics.keys() ], key=lambda x: x[0], reverse=True)
        tprint(topics)


# Helper function to make the directory
def mkdir(folder):
    try:
        os.makedirs(folder)
    except:
        pass

if __name__ == '__main__':
    master_df = main()

