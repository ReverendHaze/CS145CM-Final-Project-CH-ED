import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from math import log
import pytz
import scipy.sparse as sp

from modules.debug_module import *
import modules.ngram_module as ngram_module

def Histogram(df, city, n_days=0, n_hours=2, n_minutes=0):

    # create empty dictionary of histograms
    histograms = {}

    # define timestep
    t_step = datetime.timedelta(days=n_days, minutes=n_minutes, hours=n_hours)

    # loop over df by timestep
    t_start = pytz.utc.localize(datetime.datetime(year=2015, month=3, day=24, hour=0))
    # Three possible tmax's
    # One day after the start for testing
    #t_max = pytz.utc.localize(datetime.datetime(year=2015, month=3, day=25, hour=0))
    # End of two week window in which we have continuous data
    t_max = pytz.utc.localize(datetime.datetime(year=2015, month=4, day=7, hour=0))
    # Last tweet received
    #t_max = df.index.max()

    #n_steps = 168
    n_steps = (t_max-t_start)/t_step

    df=df[df.index >= t_start]
    df=df[df.index <= t_max]


    t_end = t_start + t_step
    i=0
    tprint('beginning while loop')
    while t_end <= t_max:

        tprint(t_end)

        # get dictionary of bigrams and their frequency within the timestep
        window_df = df[df.index < t_end]
        freq_dict = ngram_module.BuildCounter(window_df)

        # remove current timestep from df and update end of next timestep
        df = df[df.index >= t_start]
        t_start = t_end

        not_observed = list(histograms.keys())

        # add that timestep's output to main histogram dictionary
        for key in freq_dict.keys():
            value = freq_dict[key]
            if key in histograms:
                histograms[key][0,i] = value
            else:
                histograms[key] = sp.dok_matrix((1,n_steps))
                histograms[key][0,i] = value

        i=i+1
        t_end = t_start + t_step

    # Plot sensitivity of remaining bigrams vs cutoff
    plt.plot(list(map(lambda x: log(len(list(filter(lambda y: len(histograms[y]) > x, histograms.keys())))), range(i))))
    plt.savefig('graph_{}.png'.format(city))

    # Remove bigrams that don't occur in enough periods
    cutoff = 70
    #cutoff = 6
    bigrams = list(filter(lambda x: len(histograms[x]) > cutoff, histograms.keys()))
    histograms = { x: histograms[x] for x in bigrams }

    # Unite in one dataframe in csr format for easy manipulations
    tprint('Number of bigrams: {}'.format(len(bigrams)))
    df = pd.DataFrame(histograms).dropna(how='all', axis=1)

    return df



# BurstyBigrams = function to obtain list of bursty bigrams for the last timestep in a window
# inputs:
    # df = window of master_df for one city
    # n_days, n_hours, n_minutes = optional parameters to define timestep
    # cutoff = zscore above which a bigram is considered 'bursty'
# outputs:
    # bursty = a list of bursty bigrams in the last timestep
    # histograms = a dataframe of normalized frequencies

def BurstyBigrams(scores, cutoff=1.64):

    bursty = []

    for bigram in scores.columns:
        try:
            score = float(scores[bigram][len(scores[bigram])-1])
            if score >= cutoff:
                bursty.append(bigram)
        except:
            print(bigram)

    return bursty

