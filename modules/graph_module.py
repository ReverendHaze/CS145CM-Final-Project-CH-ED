# Import the necessary methods and libraries
import pandas as pd
import numpy as np
import time
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

# Simple graphing module to output a graph of the number of tweets by minute
def GraphClusteredHexbin(df, centers, city):
    latmin = df['latitude'].min()
    latmax = df['latitude'].max()
    lonmin = df['longitude'].min()
    lonmax = df['longitude'].max()

    merc_map = Basemap(projection='merc', llcrnrlat=latmin, llcrnrlon=lonmin, urcrnrlat=latmax, urcrnrlon=lonmax, resolution='h')
    merc_map.drawcoastlines()
    merc_map.drawstates()
    x, y = merc_map(df['longitude'].values, df['latitude'].values)
    merc_map.hexbin(x, y, bins='log', alpha=1.0, gridsize=750, mincnt=1)
    plt.xlabel('Longitude')
    xmin = min(x)-1
    xmax = max(x)+1
    plt.xticks(np.arange(xmin, xmax, (xmin-xmax)/5), np.arange(lonmin, lonmax, (lonmax-lonmin)/5))
    plt.subplots_adjust(bottom=0.15)
    plt.ylabel('Latitude')
    ymin = min(y)-1
    ymax = max(y)+1
    plt.yticks(np.arange(ymin, ymax, (ymax-ymin)/5), np.arange(latmin, latmax, (latmax-latmin)/5))
    plt.title('Heatmap of tweets for {}'.format(city))
    cb = plt.colorbar()
    cb.set_label('log(counts)')

    centers = list(zip(*centers))
    c_lons, c_lats = merc_map(centers[0], centers[1])
    plt.scatter(c_lons, c_lats, color='red', s=15, alpha=1.0)


    plt.savefig('{}/hex/hexmap_kmeans_{}'.format(GRAPH_FOLDER, city), dpi=300)
    plt.clf()

