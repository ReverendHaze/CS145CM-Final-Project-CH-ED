#Import the necessary methods and libraries
import pandas as pd
import pickle
import glob
import natsort
import os
import shelve
from multiprocessing import Pool
from multiprocessing import cpu_count

from modules.debug_module import Logger

POOL_WORKERS = cpu_count()

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

def MakeTweetDF(logger):
    in_files = glob.glob('{}/*.pickle'.format(DATA_FOLDER))

    if not (os.path.exists(CHICAGO_DF) and \
            os.path.exists(HOUSTON_DF) and \
            os.path.exists(LA_DF)):
        logger.tprint('Failed, creating new master pickles')
        rm(CHICAGO_DF)
        rm(HOUSTON_DF)
        rm(LA_DF)
        rm(CONFIG_FILE)
        CreateTweetDF(in_files, logger)
    else:
        config = shelve.open(CONFIG_FILE)
        converted_files = config['converted_files']
        config.close()
        logger.tprint('Files in master dataframes: {}'.format(len(converted_files)))
        logger.tprint('Files in data folder: {}'.format(len(in_files)))
        if len(in_files) > len(converted_files) + 50:
            logger.tprint('Updating with new input files...')
            return UpdateTweetDF(in_files, converted_files, logger)
        else:
            logger.tprint('Not enough new input files to warrant concatenation. Done.')


def CreateTweetDF(in_files, logger):
    p = Pool(POOL_WORKERS)
    dfs = p.map_async(TweetsToDF, in_files).get()
    p.close()
    master_df = pd.concat(dfs)
    master_df.loc[:,'city'] = master_df.apply(InCity, axis=1)

    logger.tprint('Writing master pickles to files')
    with open(CHICAGO_DF, 'wb+') as f:
        pickle.dump(master_df[master_df['city'] == 'Chicago'], f)
    logger.tprint('Wrote Chicago DF')
    with open(HOUSTON_DF, 'wb+') as f:
        pickle.dump(master_df[master_df['city'] == 'Houston'], f)
    logger.tprint('Wrote Houston DF')
    with open(LA_DF, 'wb+') as f:
        pickle.dump(master_df[master_df['city'] == 'LA'], f)
    logger.tprint('Wrote LA DF')

    config = shelve.open(CONFIG_FILE)
    config['converted_files'] = in_files
    config.close()


def UpdateTweetDF(in_files, converted_files, logger):
    logger.tprint('Updating with {} new data files'.format(len(in_files)-len(converted_files)))
    in_files = [ x for x in in_files if x not in converted_files ]
    p = Pool(POOL_WORKERS)
    dfs = p.map_async(TweetsToDF, in_files).get()
    p.close()
    logger.tprint('Concatenating files...')
    dfs = pd.concat(dfs)
    dfs.loc[:,'city'] = dfs.apply(InCity, axis=1)

    logger.tprint('Writing updated master dfs')
    df = pd.read_pickle(CHICAGO_DF)
    chicago_mask = dfs['city'] == 'Chicago'
    with open(CHICAGO_DF, 'rb+') as f:
        chi = dfs[chicago_mask]
        pickle.dump(pd.concat([df, dfs[chicago_mask]]), f)
    dfs = dfs[~chicago_mask]
    logger.tprint('Completed Chicago DF')

    df = pd.read_pickle(HOUSTON_DF)
    houston_mask = dfs['city'] == 'Houston'
    with open(HOUSTON_DF, 'rb+') as f:
        pickle.dump(pd.concat([df, dfs[houston_mask]]), f)
    dfs = dfs[~houston_mask]
    logger.tprint('Completed Houston DF')

    df = pd.read_pickle(LA_DF)
    with open(LA_DF, 'rb+') as f:
        pickle.dump(pd.concat([df, dfs]), f)
    logger.tprint('Completed LA DF')

    config = shelve.open(CONFIG_FILE)
    config['converted_files'] = in_files + converted_files
    config.close()


def TweetsToDF(tweets):
    tweets = pd.read_pickle(tweets)
    tweets_dict = {}

    #Full set of potentially interesting params
    #tweet_params = ['id', 'text', 'retweeted', 'created_at']
    #user_params = ['id', 'followers_count', 'statuses_count', \
    tweet_params = ['id', 'text', 'created_at']
    user_params = []

    for param in tweet_params:
        try:
            tweets_dict[param] = list(map(lambda twt: str(LookDefault(twt, param, None)), tweets))
        except:
            tweets_dict[param] = list(map(lambda twt: str(LookDefault(twt, param, None)), tweets))

    for param in user_params:
        tweets_dict['u_{}'.format(param)] = \
                list(map(lambda x: str(LookDefault(x, 'user', None, sec=param)), tweets))

    #Handle coordinates and hashtags separately since they require different \
    #parsing
    tweets_dict['longitude'], tweets_dict['latitude'] = \
            zip(*list(map(GetCoords, tweets)))

    #Uncomment if we ever use these
    #tweets_dict['hashtags'] = list(map(GetHashtags, tweets))
    #tweets_dict['sentiment'] = list(map(GetSentiment, tweets))
    return pd.DataFrame(tweets_dict, index=tweets_dict['id']).dropna(axis=0, how='all')


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

def LookDefault(dictionary, key, default, sec=None):
    try:
        if sec:
            return dictionary[key][sec]
        else:
            return dictionary[key]
    except:
        print('Lookup of {} failed.'.format(key))
        return default

def GetSentiment(tweet):
    try:
        twt_str = tweet['text'].split(' ')
        for token in twt_str:
            if token in SMILE_EMOTICONS + LAUGHING_EMOTICONS +\
                        SMIRK_EMOTICONS:
                return 1
            elif token in FROWN_EMOTICONS + HORROR_EMOTICONS:
                return -1
            else:
                return 0
    except:
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

def rm(filename):
    try:
        os.remove(filename)
    except:
        pass
