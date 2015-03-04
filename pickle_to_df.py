#! /bin/python

#Import the necessary methods and libraries
import json
import pandas as pd
import pickle
import glob

RESULTS_FOLDER = 'out'

def TweetsToDF(tweets):
    tweets_dict = {}
    tweet_params = ['id', 'text', 'retweeted']
    user_params = ['id', 'followers_count', 'statuses_count', \
                   'friends_count', 'lang']
    for param in tweet_params:
        tweets_dict[param] = list(map(lambda x: str(x[param]), tweets))
    for param in user_params:
        tweets_dict['u_{}'.format(param)] = \
                list(map(lambda x: str(x['user'][param]), tweets))

    #Handle coordinates and hashtags separately since they require different \
    #parsing
    tweets_dict['latitude'], tweets_dict['longitude'] = \
            zip(*list(map(GetCoords, tweets)))
    tweets_dict['hashtags'] = list(map(GetHashtags, tweets))
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

if __name__ == '__main__':
    in_files = glob.glob('{}/*.pickle'.format(RESULTS_FOLDER))
    try:
        in_files.remove('{}/master.pickle'.format(RESULTS_FOLDER))
    except:
        pass
    dfs = []
    for twt_file in in_files:
        with open(twt_file, 'rb') as f:
            df = TweetsToDF(pickle.load(f))
            dfs.append(df)
    master_df = pd.concat(dfs)
    print(master_df.head())
    with open('{}/master.pickle'.format(RESULTS_FOLDER), 'wb+') as f:
        pickle.dump(master_df, f)

