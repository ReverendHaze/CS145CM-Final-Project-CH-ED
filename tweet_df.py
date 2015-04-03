#Import the necessary methods and libraries
import pandas as pd
import pickle
import glob
import datetime

MASTER_DF_PATH = 'out/master.pickle'
DATA_FOLDER = 'out/data'

def GetTweetDF():
    try:
        with open(MASTER_DF_PATH, 'rb') as f:
            m_file_count, master_df = pickle.load(f)
            in_files = glob.glob('{}/*.pickle'.format(DATA_FOLDER))
            if len(in_files > m_file_count):
                return UpdateTweetDF(in_files, m_file_count, master_df)
            else:
                return master_df
    except:
        return CreateTweetDF()

def CreateTweetDF():
    in_files = glob.glob('{}/*.pickle'.format(DATA_FOLDER))
    dfs = map(pd.read_pickle, in_files)
    master_df = pd.concat(dfs)
    with open(master_filename, 'wb+') as f:
        pickle.dump([len(in_files), master_df], f)
    return master_df

def UpdateTweetDF(in_files, master_df_files, master_df):
    dfs = map(pd.read_pickle, sort(in_files)[master_df_files:])
    master_df = pd.concat([master_df] + dfs)
    with open(MASTER_DF_PATH, 'wb+') as f:
        pickle.dump([master_df_files + len(dfs), master_df], f)
    return master_df

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

