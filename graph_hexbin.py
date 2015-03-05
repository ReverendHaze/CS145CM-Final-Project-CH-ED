# Import the necessary methods and libraries
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
plt.style.use('ggplot')

# Simple graphing module to output a graph of the number of tweets by minute
def GraphCityHexbin(master_df, centers, output_filename):
    CHICAGO_BOX = [ -87.94,  -87.52, 41.64, 42.02]
    LA_BOX      = [-118.66, -118.16, 33.70, 34.34]
    HOUSTON_BOX = [ -95.79,  -95.01, 29.52, 30.11]
    latmin = master_df['latitude'].min()
    latmax = master_df['latitude'].max()
    lonmin = master_df['longitude'].min()
    lonmax = master_df['longitude'].max()


    plt.hexbin(master_df['longitude'], master_df['latitude'], bins='log', cmap=plt.cm.YlOrRd_r, alpha=1.0, gridsize=100)
    plt.axis([lonmin, lonmax, latmin, latmax])
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Heatmap of tweets')
    cb = plt.colorbar()
    cb.set_label('log(counts)')

    c_lons, c_lats = zip(*centers)
    plt.scatter(c_lons, c_lats, color='blue', s=50, alpha=1.0)

    plt.savefig(output_filename)
    plt.clf()

