# Import the necessary methods and libraries
import pandas as pd
import time
from matplotlib import pyplot as plt
plt.style.use('ggplot')

# Set the size of the window
WIN_SIZE_SEC = 5*60 #5 min

# Simple graphing module to output a graph of the number of tweets by minute
def GraphFreqs(master_df, output_filename):
    # Create a binned timestamp of width WIN_SIZE_SEC and count the number of entries within
    # each period.
    master_df['graph_ts'] = list(map(lambda x: GetTS(x, WIN_SIZE_SEC), master_df['created_at']))
    master_df['count'] = 1
    master_df = master_df[['created_at', 'graph_ts', 'count']]
    counts_by_ts = master_df.groupby('graph_ts').sum()

    # Attach the counts back to the main dataframe, keeping only one entry per binned period
    master_df = master_df.join(counts_by_ts, on='graph_ts', rsuffix = '_r').drop_duplicates('graph_ts')
    master_df = master_df.ix[1:-1]

    # Create a 'tweets_per_min' variable, then ready the df for graphing
    master_df['tweets_per_min'] = master_df['count_r'] / (WIN_SIZE_SEC / 60.0)
    master_df.index = pd.DatetimeIndex(master_df['created_at']).tz_convert('US/Pacific')
    master_df = master_df[['tweets_per_min']]
    master_df = master_df.sort()

    # Make the plot, add niceties and save
    ax = master_df.plot()
    ax.set_title('Tweets per minute over the data collection period')
    ax.set_xlabel('Time')
    ax.set_ylabel('Tweets per minute')
    fig = ax.get_figure()
    fig.savefig(output_filename)

#Get the timestamps of each message collapsed at a resolution of 'res' seconds
def GetTS(ts, res):
    ts = time.mktime(time.strptime(ts, '%a %b %d %H:%M:%S +0000 %Y'))
    return ts - (ts % res)

