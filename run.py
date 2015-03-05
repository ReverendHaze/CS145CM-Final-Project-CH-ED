#!/bin/python

# Prepackaged modules
import pickle
import os

# Our modules
import pickle_to_df
import graph_freqs
import graph_hexbin
import kmeans

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
    graph_filename = '{}/graph/freq/tweets_per_min.png'.format(output_folder)
    mkdir(graph_filename)
    graph_freqs.GraphFreqs(master_df, graph_filename)

    # Remove non-geocoded tweets
    master_df = master_df.dropna(subset=['longitude', 'latitude'])
    master_df = master_df[master_df.apply(InCity, axis=1)]

    (master_df, _) = kmeans.ApplyKMeans(master_df, ['longitude', 'latitude'], 3, 'city_num')
    for index, df in master_df.groupby('city_num'):
        # Graph the number of tweets within each part of each city
        (_, centers) = kmeans.ApplyKMeans(df, ['longitude', 'latitude'], 5, 'center')
        graph_filename = '{}/graph/hex/tweets_by_region_{}.png'.format(output_folder, index)
        mkdir(graph_filename)
        graph_hexbin.GraphCityHexbin(df, centers, graph_filename)

# Helper function to make the directory to a file
# First extracts the directory of the file, then
# makes that directory if it doesn't exist
def mkdir(filename):
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        pass

def InCity(tweet):
    CHICAGO_BOX = [ -87.94,  -87.52, 41.64, 42.02]
    LA_BOX      = [-118.66, -118.16, 33.70, 34.34]
    HOUSTON_BOX = [ -95.79,  -95.01, 29.52, 30.11]

    lon = tweet['longitude']
    lat = tweet['latitude']

    if (CHICAGO_BOX[0] <= lon <= CHICAGO_BOX[1]) and (CHICAGO_BOX[2] <= lat <= CHICAGO_BOX[3]):
        return True
    if (HOUSTON_BOX[0] <= lon <= HOUSTON_BOX[1]) and (HOUSTON_BOX[2] <= lat <= HOUSTON_BOX[3]):
        return True
    if (LA_BOX[0] <= lon <= LA_BOX[1]) and (LA_BOX[2] <= lat <= LA_BOX[3]):
        return True
    else:
        return False

if __name__ == '__main__':
    main()

