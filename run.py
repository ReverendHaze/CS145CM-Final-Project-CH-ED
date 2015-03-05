#!/bin/python

# Prepackaged modules
import pickle
import os

# Our modules
import pickle_to_df
import graph_freqs
import graph_hexbin

# Code to execute when the script is run
def main():
    output_folder = 'out'
    master_filename = '{}/{}.pickle'.format(output_folder, 'master')

    # If the master dataframe doesn't exist, create it and then load it.
    if not os.path.isfile(master_filename):
        pickle_to_df.CreateDF(master_filename)
    with open(master_filename, 'rb') as f:
        master_df = pickle.load(f)

    # Graph the number of tweets per minute over all data
    graph_filename = '{}/freq/tweets_per_min.png'.format(output_folder)
    mkdir(graph_filename)
    graph_freqs.GraphFreqs(master_df, graph_filename)

    # Graph the number of tweets within each part of each city
    graph_filename = '{}/hex/tweets_by_region.png'.format(output_folder)
    mkdir(graph_filename)
    graph_hexbin.GraphCityHexbin(master_df, '[City]', graph_filename)

# Helper function to make the directory to a file
# First extracts the directory of the file, then
# makes that directory if it doesn't exist
def mkdir(filename):
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        pass

if __name__ == '__main__':
    main()

