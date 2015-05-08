#Import the necessary methods and libraries
import pandas as pd
import pickle
import glob
import natsort
import os
import shelve

from modules.debug_module import *

CHICAGO_DF = 'out/chicago.pickle'
HOUSTON_DF = 'out/houston.pickle'
LA_DF = 'out/la.pickle'
DATA_FOLDER = 'out/data'
CONFIG_FILE = 'out/config.shelf'

CH_MINLON, CH_MAXLON, CH_MINLAT, CH_MAXLAT = [ -87.94,  -87.52, 41.64, 42.02]
LA_MINLON, LA_MAXLON, LA_MINLAT, LA_MAXLAT = [-118.66, -118.16, 33.70, 34.34]
HO_MINLON, HO_MAXLON, HO_MINLAT, HO_MAXLAT = [ -95.79,  -95.01, 29.52, 30.11]

# Lists of emoticons from twitter.
SMILE_EMOTICONS = [':-)', ':)', ':D', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}', ':^)']
LAUGHING_EMOTICONS = [':-D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D', '=-3', '=3', 'B^D']
SMIRK_EMOTICONS = [';-)', ';)', '*-)', '*)', ';-]', ';]', ';D', ';^)']
FROWN_EMOTICONS = ['>:[', ':-(', ':(',  ':-c', ':c', ':-<', ':<', ':-[', ':[', ':{']
HORROR_EMOTICONS = ['D:<', 'D:', 'D8', 'D;', 'D=', 'DX', 'v.v', 'D-\':']

def GetCity(city):
    if city is 'Chicago':
        master_df = pd.read_pickle(CHICAGO_DF)
    if city is 'Houston':
        master_df = pd.read_pickle(HOUSTON_DF)
    if city is 'LA':
        master_df = pd.read_pickle(LA_DF)
    return master_df

def MakeTweetDF():
    in_files = glob.glob('{}/*.pickle'.format(DATA_FOLDER))
    if not (os.path.exists(CHICAGO_DF) and \
            os.path.exists(HOUSTON_DF) and \
            os.path.exists(LA_DF)):
        CreateTweetDF(in_files)
    else:
        config = shelve.open(CONFIG_FILE)
        tprint('Files in master dataframes: {}'.format(config['converted_files']))
        tprint('Files in data folder: {}'.format(len(in_files)))
        if len(in_files) > config['converted_files'] + 24: #4 hours
            tprint('Updating with new input files...')
            return UpdateTweetDF(in_files, config['converted_files'])
        else:
            tprint('Not enough new input files to warrant concatenation. Done.')

def CreateTweetDF(in_files):
    tprint('Failed, creating new master pickles')
    dfs = list(map(lambda x: TweetsToDF(pd.read_pickle(x)), in_files))
    master_df = pd.concat(dfs)
    master_df.loc[:,'city'] = master_df.apply(InCity, axis=1)
    tprint('Writing master pickles to files')
    with open(CHICAGO_DF, 'wb+') as f:
        pickle.dump(master_df[master_df['city'] == 'Chicago'], f)
    tprint('Wrote Chicago DF')
    with open(HOUSTON_DF, 'wb+') as f:
        pickle.dump(master_df[master_df['city'] == 'Houston'], f)
    tprint('Wrote Houston DF')
    with open(LA_DF, 'wb+') as f:
        pickle.dump(master_df[master_df['city'] == 'LA'], f)
    tprint('Wrote LA DF')
    config = shelve.open(CONFIG_FILE)
    config['converted_files'] = len(in_files)
    config.close()


def UpdateTweetDF(in_files, master_df_files):
    tprint('Updating with {} new data files'.format(len(in_files)-master_df_files))
    total_files = len(in_files)
    in_files = natsort.natsorted(in_files[master_df_files:], key=lambda y: y.lower())
    dfs = []
    for index, in_file in enumerate(in_files):
        tprint('Reading file {}'.format(index))
        tweets = pd.read_pickle(in_file)
        dfs.append(TweetsToDF(tweets))
    tprint('Concatenating files...')
    dfs = pd.concat(dfs)
    dfs.loc[:,'city'] = dfs.apply(InCity, axis=1)
    tprint('Writing updated master dfs')
    with open(CHICAGO_DF, 'rb+') as f:
        df = pd.read_pickle(f)
        chicago_mask = dfs['city'] == 'Chicago'
        pickle.dump(pd.concat([df, dfs[chicago_mask]], f))
        dfs = dfs[~chicago_mask]
    tprint('Completed Chicago DF')
    with open(HOUSTON_DF, 'rb+') as f:
        df = pd.read_pickle(f)
        houston_mask = dfs['city'] == 'Houston'
        pickle.dump(pd.concat([df, dfs[houston_mask]], f))
        dfs = dfs[~houston_mask]
    tprint('Completed Houston DF')
    with open(LA_DF, 'rb+') as f:
        df = pd.read_pickle(f)
        pickle.dump(pd.concat([df, dfs], f))
    tprint('Completed LA DF')
    config = shelve.open(CONFIG_FILE)
    config['converted_files'] = len(in_files)
    config.close()

def TweetsToDF(tweets):
    tweets_dict = {}
    tweet_params = ['id', 'text', 'retweeted', 'created_at']
    user_params = ['id', 'followers_count', 'statuses_count', \
                   'friends_count', 'lang']
    for param in tweet_params:
        tweets_dict[param] = list(map(lambda x: str(x[param]), tweets))
    for param in user_params:
        tweets_dict['u_{}'.format(param)] = \
                list(map(lambda x: str(x['user'][param]), tweets))

    #Handle coordinates and hashtags separately since they require different \
    #parsing
    tweets_dict['longitude'], tweets_dict['latitude'] = \
            zip(*list(map(GetCoords, tweets)))

    tweets_dict['hashtags'] = list(map(GetHashtags, tweets))
    tweets_dict['sentiment'] = list(map(GetSentiment, tweets))

    #Filter out those tweets we got that aren't in a box
    return pd.DataFrame(tweets_dict, index=tweets_dict['id'])

def GetCoords(tweet):
    try:
        return tuple(tweet['coordinates']['coordinates'])
    except:
        return (None,None)

def GetHashtags(tweet):
    try:
        return ','.join(list(map(lambda x: x['text'], tweet['entities']['hashtags'])))
    except:
        return None

def GetSentiment(tweet):
    twt_str = tweet['text'].split(' ')
    for token in twt_str:
        if token in SMILE_EMOTICONS + LAUGHING_EMOTICONS +\
                    SMIRK_EMOTICONS:
            return 1
        elif token in FROWN_EMOTICONS + HORROR_EMOTICONS:
            return -1
        else:
            return 0

def InCity(tweet):
    try:
        lon = tweet['longitude']
        lat = tweet['latitude']
        if (CH_MINLON <= lon <= CH_MAXLON) and (CH_MINLAT <= lat <= CH_MAXLAT):
            return 'Chicago'
        if (HO_MINLON <= lon <= HO_MAXLON) and (HO_MINLAT <= lat <= HO_MAXLAT):
            return 'Houston'
        if (LA_MINLON <= lon <= LA_MAXLON) and (LA_MINLAT <= lat <= LA_MAXLAT):
            return 'LA'
    except:
        pass
    return 'Other'

