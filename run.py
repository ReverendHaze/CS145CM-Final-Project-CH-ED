#!/bin/python

# Prepackaged modules
import pickle
import os

# Our modules
import tweet_df
import graph_module
import cluster_module
import ngram_module

# Code to execute when the script is run
def main():

    # Get the dataframe of all tweets, creating it from
    # the data files if necessary and building
    # incrementally with new files.
    master_df = tweet_df.GetTweetDF()

    # Graph the number of tweets per minute over all data
    graph_module.GraphFreqs(master_df)

    # (Uncomment/Comment) to (restore/remove) datapoints outside of the
    # three desired cities from the dataset.
    master_df = master_df[master_df['City'] != 'Other']

    #function to get dictionary of histograms for a given city and time window
    def get_histograms(city, n_days=0, n_hours=1, n_minutes=0):

        master_df = master_df.loc[(master_df['City']==city), 'text']

        t_step = datetime.timedelta(days=n_days, minutes=n_minutes, hours=n_hours)

        # create empty dictionary
        histograms = {}

        # loop over master_df by timestep
        t_start = master_df.DatetimeIndex.min()
        t_max = master_df.DatetimeIndex.max()

        while t_start <= t_max:
            t_end = t_start + t_step

            # get dictionary of bigrams and their frequency within the timestep
            freq_dict = gram_module.function(master_df[master_df.index < t_end])

            # remove current timestep from master_df and update end of next timestep
            master_df = master_df[master_df.index >= t_start]
            t_start = t_end

            # add that timestep's output to main histogram dictionary
            for key, value in freq_dict.iteritems():
                if key in histograms:
                    histograms[key] = histograms[key].append(value)
                else:
                    histograms[key] = np.array([value])

        #return completed dictionary of histogram vectors
        return histograms


    for index, df in master_df.groupby('City'):
        # Graph tweet rate over time
        graph_module.GraphFreqs(df, city=index)

        # Graph the number of tweets within each part of each city
        centers = cluster_module.ApplyKMeans(df, ['longitude', 'latitude'], 6)
        graph_module.GraphClusteredHexbin(df, centers, index)
    return master_df



# Helper function to make the directory
def mkdir(folder):
    try:
        os.makedirs(folder)
    except:
        pass

if __name__ == '__main__':
    master_df = main()

