# Import the necessary methods and libraries
import pandas as pd
from matplotlib import pyplot as plt
plt.style.use('ggplot')

# Simple graphing module to output a graph of the number of tweets by minute
def GraphCityHexbin(master_df, city, output_filename):
    latmin = master_df['latitude'].min()
    latmax = master_df['latitude'].max()
    lonmin = master_df['longitude'].min()
    lonmax = master_df['longitude'].max()

    ax = plt.hexbin(master_df['latitude'], master_df['longitude'])
    plt.axis([lonmin, lonmax, latmin, latmax])
    fig = ax.get_figure()
    fig.suptitle('Heatmap of tweets for city {}'.format(city))
    fig.savefig(output_filename)
    plt.clf()

