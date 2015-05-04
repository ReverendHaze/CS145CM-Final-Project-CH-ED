import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering

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

def GetClusters(df, city, n_clusters, how='kmeans'):

    # reduce df to features of interest
    df = df.dropna(how='any', subset=columns)
    reduced = df[columns]

    # convert features of interest to np.float64 format
    reduced = reduced.convert_objects(convert_numeric=True)

    # initialize and fit model
    model = []
    if how is 'kmeans':
        model = KMeans(n_clusters=n_clusters, init='k-means++')
        how = 'KMeans'
    elif how is 'spectral':
        model = SpectralClustering(n_clusters=n_clusters, eigen_solver='arpack', affinity='nearest_neighbors')
        how = 'Spectral'

    model.fit(reduced)

    # get cluster labels for each data point
    labels = model.labels_

    # add labels to master data frame
    df[cluster_column]=labels

    graph_module.GraphClusters(df, city, how)

