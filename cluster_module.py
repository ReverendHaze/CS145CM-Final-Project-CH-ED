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

def ApplyKMeans(df, column_list, n_clusters, cluster_column=None):

    # reduce df to features of interest
    df = df.dropna(subset=column_list)
    reduced = df[column_list]

    # convert features of interest to np.float64 format
    reduced = reduced.convert_objects(convert_numeric=True)

    # initialize and fit KMeans model
    model = KMeans(n_clusters=n_clusters, init='k-means++')
    model.fit(reduced)

    # get cluster centers
    centers = model.cluster_centers_

    if cluster_column is None:
        return centers
    else:
        # get cluster labels for each data point
        labels = model.labels_

        # add labels to master data frame
        df[cluster_column]=labels

        return(centers, df)

