#! /bin/python

#Import the necessary methods and libraries
import pandas as pd
import pickle
import time
from matplotlib import pyplot as plt

RESULTS_FOLDER = 'out'
WIN_SIZE_SEC = 15

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
    master_df = master_df[['graph_ts', 'count']]
    res_df = master_df.groupby('graph_ts').sum()
    fig = res_df.plot().get_figure()
    fig.savefig('res.png')

