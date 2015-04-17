#!/bin/python

# Prepackaged modules
import pickle
import os

# Our modules
import tweet_df
import graph_module
import cluster_module

# Code to execute when the script is run
def main():

    # Get the dataframe of all tweets, creating it from
    # the data files if necessary and building
    # incrementally with new files.
    master_df = tweet_df.GetTweetDF()

    # Graph the number of tweets per minute over all data
    graph_module.GraphFreqs(master_df)

    # Remove non-geocoded tweets
    master_df = master_df.dropna(subset=['longitude', 'latitude'])
    master_df['City'] = master_df.apply(InCity, axis=1)

    # (Uncomment/Comment) to (restore/remove) datapoints outside of the
    # three desired cities from the dataset.
    master_df = master_df[master_df['City'] != 'Other']

    for index, df in master_df.groupby('City'):
        # Graph tweet rate over time
        graph_module.GraphFreqs(df, city=index)

        # Graph the number of tweets within each part of each city
        centers = cluster_module.ApplyKMeans(df, ['longitude', 'latitude'], 6)
        graph_module.GraphClusteredHexbin(df, centers, index)

# Helper function to make the directory
def mkdir(folder):
    try:
        os.makedirs(folder)
    except:
        pass

def InCity(tweet):
    ch_minlon, ch_maxlon, ch_minlat, ch_maxlat = [ -87.94,  -87.52, 41.64, 42.02]
    la_minlon, la_maxlon, la_minlat, la_maxlat = [-118.66, -118.16, 33.70, 34.34]
    ho_minlon, ho_maxlon, ho_minlat, ho_maxlat = [ -95.79,  -95.01, 29.52, 30.11]

    lon = tweet['longitude']
    lat = tweet['latitude']

    if (ch_minlon <= lon <= ch_maxlon) and (ch_minlat <= lat <= ch_maxlat):
        return 'Chicago'
    if (ho_minlon <= lon <= ho_maxlon) and (ho_minlat <= lat <= ho_maxlat):
        return 'Houston'
    if (la_minlon <= lon <= la_maxlon) and (la_minlat <= lat <= la_maxlat):
        return 'LA'
    else:
        return 'Other'

if __name__ == '__main__':
    main()

