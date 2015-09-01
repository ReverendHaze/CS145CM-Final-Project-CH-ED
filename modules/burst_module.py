import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from math import log
import pytz
import scipy.sparse as sp
from multiprocessing import Pool
from multiprocessing import cpu_count

from modules.debug_module import *
import modules.ngram_module as ngram_module

T_START = pytz.utc.localize(datetime.datetime(year=2015, month=3, day=24, hour=0))
T_STEP_MIN = 30 # Must be factor of 60

#PERIOD_CUTOFF = 20
PERIOD_CUTOFF = 3

def Histogram(df, city):

    # create empty dictionary of histograms
    histograms = {}

    # loop over df by timestep
    # Three possible tmax's
    # One day after the start for testing
    #t_max = pytz.utc.localize(datetime.datetime(year=2015, month=3, day=25, hour=0))
    # End of two week window in which we have continuous data
    t_max = pytz.utc.localize(datetime.datetime(year=2015, month=4, day=7, hour=0))
    # Last tweet received
    #t_max = df.index.max().astimezone('utc')

    # Screen out values outside of our window
    tprint('Cutting DataFrame down to {} - {}'.format(T_START, t_max))
    df = df[df.index >= T_START]
    df = df[df.index <= t_max]

    # Group to the nearest 30 minutes
    tprint('Partitioning dataframe')
    df = df.groupby([df.index.year, df.index.month, df.index.day, \
                     df.index.hour, df.index.minute - (df.index.minute % T_STEP_MIN)])
    df = [ value for key, value in df ]
    tprint('Partitions: {}'.format(len(df)))


    tprint('Dataframe partitioned, building counters')

    # Build a list of (word, frequency) dictionaries, one for each
    # partition of the dataframe. Then convert these dictionaries to a
    # dataframe.
    p = Pool(cpu_count())
    tprint('Building counters')
    df = p.map_async(ngram_module.BuildCounter, df).get()
    tprint('Converting to DataFrames')
    df = p.map_async(FreqDictToDF, enumerate(df)).get()
    p.close()

    tprint('Combining DataFrames')
    ret = pd.DataFrame(df.pop(0))
    for index in np.arange(len(df)-1):
        ret = pd.concat([ret, df.pop(0)], axis=1)
        tprint(ret.shape)
    #df = pd.concat(df, axis=0, join='outer').fillna(0)

    # Remove bigrams that don't occur in enough periods
    ret['counts'] = ret.apply(lambda x: x.sum()/(x != 0).sum(), axis=0)
    ret = ret[ret['counts'] > PERIOD_CUTOFF]
    del ret['counts']

    # Unite in one dataframe and standardize by column standard deviation.
    ret = ret.apply(lambda x: x/x.std(),axis=0)
    tprint(df.shape)

    return ret.to_sparse(fill_value=0)


def FreqDictToDF(key_dict):
    (key, hist_slice) = key_dict
    d = pd.DataFrame.from_dict(hist_slice, orient='index')
    try:
        d.columns = [key]
        return d
    except:
        return pd.DataFrame()

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
            tprint(bigram)

    return bursty

