import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering

# PlotClusters is a function that applies the scikit-learn implementation of KMeans on a pandas dataframe. It implements two clustering techniques:
    #k-means:
        #using "k-means++" cluster center initialization, which balances the desire for spread-out cluster
        #center initializations and the desire to center clusters within areas densely populated by data points
    #spectral:
# inputs:
    #master_df is a pandas dataframe
    #column_list is a list of (numeric) columns of master_df; these columns are the features kmeans will use
    #n_clusters is the number of clusters for kmeans to use
    #cluster_column is the name of the column to be added to master_df and populated with integer cluster labels, resulting from kmeans
# output:
    # a pair of objects:
        # master_df, the input data frame with cluster_column added and populated and all rows with NaN values in column_list removed
        # centers, a (n_clusters)x(len(column_list)) array containing the locations of the cluster centers
def PlotClusters(df, columns, n_clusters, cluster_column, how):

    # reduce df to features of interest
    df = df.dropna(how='any', subset=columns)
    reduced = df[columns]

    # convert features of interest to np.float64 format
    reduced = reduced.convert_objects(convert_numeric=True)

    # initialize and fit model
    model = []
    if how is 'kmeans':
        model = KMeans(n_clusters=n_clusters, init='k-means++')
    elif how is 'spectral':
        model = SpectralClustering(n_clusters=n_clusters, eigen_solver='arpack', affinity='nearest_neighbors')

    model.fit(reduced)

    # get cluster centers
    centers = model.cluster_centers_

    if columns is None:
        return (centers, df)
    else:
        # get cluster labels for each data point
        labels = model.labels_

        # add labels to master data frame
        df[cluster_column]=labels

        return(centers, df)

