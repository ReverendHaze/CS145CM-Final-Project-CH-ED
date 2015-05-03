#!/bin/python

# Prepackaged modules
import pickle
import os

# Our modules
import tweet_df
import graph_module
import cluster_module
import ngram_module
import burst_module
import datetime
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

    all_bursty = {}
    for city in 'Chicago', 'Houston', 'LA':
        master_df = tweet_df.GetCity(city)
        master_df['id'] = master_df.index
        master_df.index = master_df['created_at'].apply(lambda x: datetime.datetime.strptime(x, "%a %b %d %H:%M:%S %z %Y"))
        # Get bursty bigrams for most recent period and overall zscores

        with open('out/hist/{}.pickle'.format(city), 'wb+') as f:
            pickle.dump(burst_module.Histogram(master_df, city), f)

        all_bursty[city] = burst_module.BurstyBigrams(master_df)
        # Graph tweet rate over time
        graph_module.GraphFreqs(master_df, city=city)

        # Graph the number of tweets within each part of each city
        k_cen, master_df = cluster_module.PlotClusters(master_df, ['longitude', 'latitude'], 6, 'k_centers', 'kmeans')
        #s_cen, master_df = cluster_module.PlotClusters(master_df, ['longitude', 'latitude'], 6, 's_centers', 'spectral')
        #graph_module.GraphClusteredHexbin(master_df, centers, city)


# Helper function to make the directory
def mkdir(folder):
    try:
        os.makedirs(folder)
    except:
        pass

if __name__ == '__main__':
    master_df = main()

