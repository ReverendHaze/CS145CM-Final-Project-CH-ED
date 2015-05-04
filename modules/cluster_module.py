import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from random import sample
import modules.graph_module as graph_module

# GetClusters is a function that applies the scikit-learn implementation of KMeans on a pandas dataframe. It implements two clustering techniques:
    #k-means:
        #using "k-means++" cluster center initialization, which balances the desire for spread-out cluster
        #center initializations and the desire to center clusters within areas densely populated by data points
    #spectral:
# inputs:
    #master_df is a pandas dataframe
    #city is a string
    #column_list is a list of (numeric) columns of master_df; these columns are the features kmeans will use
    #n_clusters is the number of clusters for kmeans to use
    #how is a string
# output:
    #saves desired graphs to output folder in graph folder

def GetClusters(df, city, columns= ['latitude', 'longitude'], n_clusters=12, how='kmeans'):

    print('beginning GetClusters')
    # convert features of interest to np.float64 format
    df = df.dropna(how='any')
    df = df[columns]
    df = df.convert_objects(convert_numeric=True)

    print('initialize and fit model')
    # initialize and fit model
    model = []
    if how is 'kmeans':
        model = KMeans(n_clusters=n_clusters, init='k-means++')
        how = 'KMeans'
    elif how is 'spectral':
        rand_indices = np.array(sample(range(len(df)), 50000))
        df = df.ix[rand_indices]

        model = SpectralClustering(n_clusters=n_clusters, eigen_solver='arpack', affinity='nearest_neighbors')
        how = 'Spectral'

    model.fit(df)
    print('model fitted')

    # get cluster labels for each data point
    labels = model.labels_

    # add labels to master data frame
    df['cluster_column']=labels

    print('calling graph_module')
    graph_module.GraphClusters(df, city, how)

