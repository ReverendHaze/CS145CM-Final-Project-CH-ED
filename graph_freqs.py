#! /bin/python

#Import the necessary methods and libraries
import pandas as pd
import pickle
import glob

RESULTS_FOLDER = '../out'

if __name__ == '__main__':
    df_file = '{}/master.pickle'.format(RESULTS_FOLDER)
    with open(df_file, 'rb') as f:
        master_DF = pickle.load(df_file)
    master_DF['count'] = 1

