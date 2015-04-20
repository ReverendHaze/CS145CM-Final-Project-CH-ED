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

    # Remove non-geocoded tweets
    master_df = master_df.dropna(subset=['longitude', 'latitude'])
    master_df['City'] = master_df.apply(InCity, axis=1)

    # (Uncomment/Comment) to (restore/remove) datapoints outside of the
    # three desired cities from the dataset.
    master_df = master_df[master_df['City'] != 'Other']

    # BurstyBigrams = function to obtain list of bursty bigrams for the last timestep in a window
    # inputs:
        # df = window of master_df for one city
        # n_days, n_hours, n_minutes = optional parameters to define timestep
        # cutoff = zscore above which a bigram is considered 'bursty'

    def BurstyBigrams(df, n_days=0, n_hours=1, n_minutes=0, cutoff=1.64):

        # create empty dictionary of histograms
        histograms = {}

        # define timestep
        t_step = datetime.timedelta(days=n_days, minutes=n_minutes, hours=n_hours)

        # loop over df by timestep
        t_start = df.DatetimeIndex.min()
        t_max = df.DatetimeIndex.max()

        i=0
        while t_start <= t_max:
            t_end = t_start + t_step

            # get dictionary of bigrams and their frequency within the timestep
            freq_dict = ngram_module.BuildCounter(df[df.index < t_end])

            # remove current timestep from df and update end of next timestep
            df = df[df.index >= t_start]
            t_start = t_end

            # add that timestep's output to main histogram dictionary
            for key, value in freq_dict.iteritems():
                if key in histograms:
                    histograms[key][i] = value
                else:
                    histograms[key] = np.zeros(i).append(value)
            i=i+1

        #calculate zscores and burstiness
        histograms = pd.DataFrame.from_dict(histograms)
        histograms = (histograms-histograms.mean())/histograms.std(axis=1)
        bursty = []

        for bigram in histograms.columns:
            zscore = histograms[bigram][len(histograms[bigram]-1]
            if zscore >= cutoff:
                bursty.append(bigram)

        return bursty



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
    master_df = main()

