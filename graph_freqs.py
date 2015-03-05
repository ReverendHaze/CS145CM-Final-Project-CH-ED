#! /bin/python

#Import the necessary methods and libraries
import pandas as pd
import pickle
import time
from matplotlib import pyplot as plt

RESULTS_FOLDER = 'out'
WIN_SIZE_SEC = 10*60

#Get the timestamps of each message collapsed at a resolution of 'res' seconds
def GetTS(ts, res):
    ts = time.mktime(time.strptime(ts, '%a %b %d %H:%M:%S +0000 %Y'))
    return ts - (ts % res)

if __name__ == '__main__':
    df_file = '{}/master.pickle'.format(RESULTS_FOLDER)
    with open(df_file, 'rb') as f:
        master_df = pickle.load(f)
    master_df['graph_ts'] = list(map(lambda x: GetTS(x, WIN_SIZE_SEC), master_df['created_at']))
    master_df['count'] = 1
    master_df = master_df[['created_at', 'graph_ts', 'count']]
    counts_by_ts = master_df.groupby('graph_ts').sum()
    print(counts_by_ts.head())
    master_df = master_df.join(counts_by_ts, on='graph_ts', rsuffix = '_r').drop_duplicates('graph_ts')
    master_df = master_df.ix[1:-1]
    master_df.index = pd.DatetimeIndex(master_df['created_at']).tz_convert('US/Pacific')
    master_df = master_df.sort()
    master_df['tweets_per_min'] = master_df['count_r'] / (WIN_SIZE_SEC / 60.0)
    master_df = master_df[['tweets_per_min']]
    fig = master_df.plot().get_figure()
    fig.savefig('tweets_per_min_over_time.png')

