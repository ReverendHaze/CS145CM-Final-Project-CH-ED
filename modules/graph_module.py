# Import the necessary methods and libraries
import pandas as pd
import numpy as np
import time
import matplotlib.cm as cm
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
plt.style.use('ggplot')

GRAPH_FOLDER = 'out/graph'

# Simple graphing module to output a graph of the number of tweets by minute
def GraphFreqs(df, city=None, win_size_sec=300):
    # Create a binned timestamp of width win_size_sec and count the number of entries within
    # each period.
    df['graph_ts'] = list(map(lambda x: GetTS(x, win_size_sec), df['created_at']))
    df['count'] = 1
    df = df[['created_at', 'graph_ts', 'count']]
    counts_by_ts = df.groupby('graph_ts').sum()

    # Attach the counts back to the main dataframe, keeping only one entry per binned period
    df = df.join(counts_by_ts, on='graph_ts', rsuffix = '_r').drop_duplicates('graph_ts')
    df = df.ix[1:-1]

    # Create a 'tweets_per_min' variable, then ready the df for graphing
    df['tweets_per_min'] = df['count_r'] / (win_size_sec / 60.0)
    df.index = pd.DatetimeIndex(df['created_at'])
    df = df[['tweets_per_min']]
    df = df.sort()

    # Make the plot, add niceties and save
    ax = df.plot()
    ax.set_xlabel('Time')
    ax.set_ylabel('Tweets per minute')
    if city is None:
        ax.set_title('Global recorded tweets per minute')
        output_filename = '{}/freq/global_tweets_per_minute.png'.format(GRAPH_FOLDER)
    else:
        ax.set_title('Recorded geocoded tweets per minute in {}'.format(city))
        output_filename = '{}/freq/{}_tweets_per_minute.png'.format(GRAPH_FOLDER, city)
    fig = ax.get_figure()
    fig.savefig(output_filename)
    plt.clf()

#Get the timestamps of each message collapsed at a resolution of 'res' seconds
def GetTS(ts, res):
    ts = time.mktime(time.strptime(ts, '%a %b %d %H:%M:%S +0000 %Y'))
    return ts - (ts % res)



# Simple graphing module to output a plot of either the hexbinned data points or the color-coded, clustered data points

def GraphHexbin(df, city):

    MapSetUp(df, hexbin_or_cluster=hexbin, city=city)


def GraphClusters(df, city, how):

    MapSetUp(df, hexbin_or_cluster=hexbin, city=city, how)


def MapSetUp(df, hexbin_or_cluster, city, how):

    latmin = df['latitude'].min()
    latmax = df['latitude'].max()
    lonmin = df['longitude'].min()
    lonmax = df['longitude'].max()

    merc_map = Basemap(projection='merc', llcrnrlat=latmin, llcrnrlon=lonmin, urcrnrlat=latmax, urcrnrlon=lonmax, resolution='h')
    merc_map.drawcoastlines()
    merc_map.drawstates()

    x, y = merc_map(df['longitude'].values, df['latitude'].values)

    plt.xlabel('Longitude')
    xmin = min(x)-1
    xmax = max(x)+1
    plt.xticks(np.arange(xmin, xmax, (xmin-xmax)/5), np.arange(lonmin, lonmax, (lonmax-lonmin)/5))
    plt.subplots_adjust(bottom=0.15)
    plt.ylabel('Latitude')
    ymin = min(y)-1
    ymax = max(y)+1
    plt.yticks(np.arange(ymin, ymax, (ymax-ymin)/5), np.arange(latmin, latmax, (latmax-latmin)/5))

    if hex_or_cluster == hexbin:
        merc_map.hexbin(x, y, bins='log', alpha=1.0, gridsize=750, mincnt=1)
        plt.title('Heatmap of tweets for {}'.format(city))
        cb = plt.colorbar()
        cb.set_label('log(counts)')

        plt.savefig('{}/hex/hexmap_{}'.format(GRAPH_FOLDER, city), dpi=300)
        plt.clf()

    else:
        labels = df.cluster_column.unique()
        plt.title('{}-Clustered tweets for {}'.format(how, city))

        colors = iter(cm.Set2(np.linspace(0, 1, len(labels))))

        for number, label in enumerate(labels):

            c = colors[number]
            reduced_df = df[df[cluster_column==label]]

            x, y = merc_map(reduced_df['longitude'].values, reduced_df['latitude'].values)
            plt.scatter(x, y, color=c, s=15, alpha=1.0)

        plt.savefig('{}/cluster/hexmap_{}_{}'.format(GRAPH_FOLDER, how, city), dpi=300)
        plt.clf()


