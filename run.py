#!/bin/python

# Prepackaged modules
import pickle
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np

# Our modules
import tweet_df
import graph_module
import cluster_module
import ngram_module
import burst_module
import dimension_module as dim_module
from debug_module import *

# Code to execute when the script is run
def main():

    # Build the dataframes for all tweets, creating
    # them from the data files if necessary and building
    # incrementally with new files.
    tweet_df.MakeTweetDF()

    # define dictionaries for bursty tweet lists and zscore dfs

    master_df = tweet_df.GetCity('Chicago')
    master_df['id'] = master_df.index
    f_string = "%a %b %d %H:%M:%S %z %Y"
    master_df.index = master_df['created_at'].apply(lambda x: datetime.datetime.strptime(x, f_string))

    for city in 'Chicago', 'Houston', 'LA':
        master_df = tweet_df.GetCity(city)
        master_df['id'] = master_df.index
        master_df.index = master_df['created_at'].apply(lambda x: datetime.datetime.strptime(x, "%a %b %d %H:%M:%S %z %Y"))

        # Graph tweet rate over time
        graph_module.GraphFreqs(master_df, city=city)

        # Graph the number of tweets within each part of each city
        k_cen, master_df = cluster_module.PlotClusters(master_df, ['longitude', 'latitude'], 6, 'k_centers', 'kmeans')
        #s_cen, master_df = cluster_module.PlotClusters(master_df, ['longitude', 'latitude'], 6, 's_centers', 'spectral')
        #graph_module.GraphClusteredHexbin(master_df, centers, city)

        hist_mat = burst_module.Histogram(master_df, city).as_matrix()
        hist_rank = np.linalg.matrix_rank(hist_mat)
        # Sensitivity analysis for reconstruction error of dimensionality reduction
        for method in ['NMF', 'PCA']:
            err = map(lambda x: dim_module.ReduceDimension(hist_mat, x, method),
                                                           range(hist_rank))
            plt.plot(range(hist_rank), err)
            plt.savefig('out/graph/{}_err.png'.format(method))



# Helper function to make the directory
def mkdir(folder):
    try:
        os.makedirs(folder)
    except:
        pass

if __name__ == '__main__':
    master_df = main()

