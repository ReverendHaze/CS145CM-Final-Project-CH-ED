#!/bin/python

# Prepackaged modules
import pickle
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np

# Our modules
import modules.tweet_df as tweet_df
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

    # define dictionaries for bursty tweet lists and zscore dfs
    for city in 'Chicago', 'Houston', 'LA':
        master_df = tweet_df.GetCity(city)
        master_df['id'] = master_df.index
        tprint('Tweets for {}: {}'.format(city, len(master_df.index)))
        if len(master_df.index.values) > SAMPLE_SIZE:
            sample_ids = np.random.choice(master_df.index.values, SAMPLE_SIZE)
            master_df = master_df.ix[sample_ids]
            tprint('Cut down to {} tweets'.format(SAMPLE_SIZE))
        master_df.index = master_df['created_at'].apply(lambda x: datetime.datetime.strptime(x, "%a %b %d %H:%M:%S %z %Y"))

        # Graph tweet rate over time
        graph_module.GraphFreqs(master_df, city=city)

        # Graph the number of tweets within each part of each city
        k_cen, master_df = cluster_module.PlotClusters(master_df, ['longitude', 'latitude'], 6, 'k_centers', 'kmeans')
        #s_cen, master_df = cluster_module.PlotClusters(master_df, ['longitude', 'latitude'], 6, 's_centers', 'spectral')
        graph_module.GraphClusteredHexbin(master_df, k_cen, city)

        hist_mat = burst_module.Histogram(master_df, city).as_matrix()
        hist_rank = np.linalg.matrix_rank(hist_mat)
        tprint('Current matrix dimensions: {}'.format(hist_mat.shape))
        tprint('Pre-reduction matrix rank: {}'.format(hist_rank))
        # Sensitivity analysis for reconstruction error of dimensionality reduction
        for method in ['NMF', 'PCA']:
            tprint('Starting {} sensitivity analysis'.format(method))
            model = dim_module.GetTrainedModel(hist_mat, hist_rank, method)
            #dim_module.GetReductionErrors(model, hist_mat, 20)
            #plt.plot(err)
            #plt.savefig('out/graph/dimensionality/{}_{}_err.png'.format(city, method))


# Helper function to make the directory
def mkdir(folder):
    try:
        os.makedirs(folder)
    except:
        pass

if __name__ == '__main__':
    master_df = main()

