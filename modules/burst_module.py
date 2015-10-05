import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from math import log
import pytz
import scipy.sparse as sp
from multiprocessing import Pool
from multiprocessing import cpu_count

from modules.debug_module import Logger
import modules.ngram_module as ngram_module

class BurstModule:
    logger = None


    def __init__(self, logger):
        self.logger = logger


    def Histogram(self, df, city, config, how='std'):
        # create empty dictionary of histograms
        histograms = {}

        # loop over df by timestep
        t_start = pytz.utc.localize(datetime.datetime(year=config['T_START_YEAR'], month=config['T_START_MONTH'], day=config['T_START_DAY']))
        t_max = pytz.utc.localize(datetime.datetime(year=config['T_MAX_YEAR'], month=config['T_MAX_MONTH'], day=config['T_MAX_DAY']))

        # Screen out values outside of our window
        self.logger.tprint('Cutting DataFrame down to {} - {}'.format(t_start, t_max))
        df = df[df.index >= t_start]
        df = df[df.index <= t_max]

        # Group to the nearest 30 minutes
        self.logger.tprint('Partitioning dataframe')
        df = df.groupby([df.index.year, df.index.month, df.index.day, \
                         df.index.hour, df.index.minute - (df.index.minute % config['T_STEP_MIN'])])
        df = [ value for key, value in df ]
        self.logger.tprint('Partitions: {}'.format(len(df)))

        self.logger.tprint('Dataframe partitioned, building counters')

        # Build a list of (word, frequency) dictionaries, one for each
        # partition of the dataframe. Then convert these dictionaries to a
        # dataframe.
        p = Pool(cpu_count())
        self.logger.tprint('Building counters')
        df = p.map_async(ngram_module.BuildCounter, df).get()
        self.logger.tprint('Converting to DataFrames')
        df = p.map_async(FreqDictToDF, enumerate(df)).get()
        p.close()

        self.logger.tprint('Combining DataFrames')
        ret = pd.DataFrame(df.pop(0))
        for _ in np.arange(len(ret)):
            try:
                ret = pd.concat([ret, df.pop(0)], axis=1)
            except:
                pass
        self.logger.tprint('Shape after combining dataframes: {}'.format(ret.shape))


        # Transform data using tf-idf
        #ret = ret.div(ret.std(axis=1), axis=0)
        periods = ret.shape[1]
        ret['periods'] = ret.count(axis=1)
        ret = ret.div(np.log(periods/ret.periods), axis='index')
        del ret['periods']
        self.logger.tprint('Shape after tf-idf: {}'.format(ret.shape))


        ret = ret[~(ret == 0).all(axis=1)]
        self.logger.tprint('Remaining bigrams: {}'.format(ret.shape[0]))

        return ret.fillna(0).to_sparse(fill_value=0)


    def FreqDictToDF(self, key_dict):
        (key, hist_slice) = key_dict
        d = pd.DataFrame.from_dict(hist_slice, orient='index')
        try:
            d.columns = [key]
            return d
        except:
            return pd.DataFrame()

