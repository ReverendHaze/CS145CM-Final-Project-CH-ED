import pandas as pd
import numpy as np
from sklearn.cluster import KMeans


# ApplyKMeans is a function that applies the scikit-learn implementation of KMeans on a pandas dataframe,
    #using "k-means++" cluster center initialization, which balances the desire for spread-out cluster
    #center initializations and the desire to center clusters within areas densely populated by data points
# inputs:
    #master_df is a pandas dataframe
    #column_list is a list of (numeric) columns of master_df; these columns are the features kmeans will use
    #n_clusters is the number of clusters for kmeans to use
    #cluster_column is the name of the column to be added to master_df and populated with integer cluster labels, resulting from kmeans
# output:
    # a pair of objects:
        # master_df, the input data frame with cluster_column added and populated and all rows with NaN values in column_list removed
        # centers, a (n_clusters)x(len(column_list)) array containing the locations of the cluster centers

def ApplyKMeans(master_df, column_list, n_clusters, cluster_column):

    # reduce df to features of interest
    master_df = master_df.dropna(subset=column_list)
    master_reduced = master_df[column_list]

    # convert features of interest to np.float64 format
    for column in column_list:
        master_reduced[column]=master_reduced[column].astype(np.float64)

    # initialize and fit KMeans model
    model = KMeans(n_clusters=n_clusters, init='k-means++')
    model.fit(master_reduced)

    # get cluster labels for each data point
    labels = model.labels_

    # add labels to master data frame
    master_df[cluster_column]=labels

    # get cluster centers
    centers = model.cluster_centers_

    return(master_df, centers)



