# Import the necessary methods and libraries
import pandas as pd
import numpy as np
import time
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
plt.style.use('ggplot')

# Simple graphing module to output a graph of the number of tweets by minute
def GraphFreqs(df, output_folder, city=None, win_size_sec=90):
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
    df.index = pd.DatetimeIndex(df['created_at']).tz_convert('US/Pacific')
    df = df[['tweets_per_min']]
    df = df.sort()

    # Make the plot, add niceties and save
    ax = df.plot()
    ax.set_xlabel('Time')
    ax.set_ylabel('Tweets per minute')
    if city is None:
        ax.set_title('Global recorded tweets per minute')
        output_filename = '{}/global_tweets_per_minute.png'.format(output_folder)
    else:
        ax.set_title('Recorded geocoded tweets per minute in {}'.format(city))
        output_filename = '{}/{}_tweets_per_minute.png'.format(output_folder, city)
    fig = ax.get_figure()
    fig.savefig(output_filename)
    plt.clf()

#Get the timestamps of each message collapsed at a resolution of 'res' seconds
def GetTS(ts, res):
    ts = time.mktime(time.strptime(ts, '%a %b %d %H:%M:%S +0000 %Y'))
    return ts - (ts % res)

# Simple graphing module to output a graph of the number of tweets by minute
def GraphClusteredHexbin(df, centers, output_folder, city):
    latmin = df['latitude'].min()
    latmax = df['latitude'].max()
    lonmin = df['longitude'].min()
    lonmax = df['longitude'].max()

    #plt.hexbin(df['longitude'], df['latitude'], bins='log', cmap=plt.cm.YlOrRd_r, alpha=1.0, gridsize=100)
    #plt.axis([lonmin, lonmax, latmin, latmax])
    print([lonmin, lonmax, latmin, latmax])
    merc_map = Basemap(projection='merc', llcrnrlat=latmin, llcrnrlon=lonmin, urcrnrlat=latmax, urcrnrlon=lonmax, resolution='h')
    merc_map.drawcoastlines()
    merc_map.drawcountries()
    merc_map.drawstates()
    merc_map.hexbin(df['longitude'], df['latitude'], bins='log', cmap=plt.cm.YlOrRd_r, alpha=1.0, gridsize=200)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Heatmap of tweets for {}'.format(city))
    cb = plt.colorbar()
    cb.set_label('log(counts)')

    c_lons, c_lats = zip(*centers)
    plt.scatter(c_lons, c_lats, color='blue', s=50, alpha=1.0)

    plt.savefig('{}/hexmap_{}'.format(output_folder, city))
    plt.clf()
