#Import the necessary methods and libraries
import pandas as pd
import pickle
import glob
import natsort

MASTER_DF_PATH = 'out/master.pickle'
DATA_FOLDER = 'out/data'

# Lists of emoticons from twitter.
SMILE_EMOTICONS = [':-)', ':)', ':D', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}', ':^)']
LAUGHING_EMOTICONS = [':-D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D', '=-3', '=3', 'B^D']
SMIRK_EMOTICONS = [';-)', ';)', '*-)', '*)', ';-]', ';]', ';D', ';^)']
FROWN_EMOTICONS = ['>:[', ':-(', ':(',  ':-c', ':c', ':-<', ':<', ':-[', ':[', ':{']
HORROR_EMOTICONS = ['D:<', 'D:', 'D8', 'D;', 'D=', 'DX', 'v.v', 'D-\':']


def GetTweetDF():
    in_files = glob.glob('{}/*.pickle'.format(DATA_FOLDER))
    try:
        print('Attempting to open master pickle')
        with open(MASTER_DF_PATH, 'rb') as f:
            (m_file_count, master_df) = pickle.load(f)
            print('Loaded master pickle')
            print('Files in master dataframe: {}'.format(m_file_count))
            print('Files in data folder: {}'.format(len(in_files)))
            if len(in_files) > m_file_count + 24*6:#One day
                print('Updating with new input files...')
                return UpdateTweetDF(in_files, m_file_count, master_df)
            else:
                print('Not enough new input files to warrant concatenation. Continuing.')
                return master_df
    except:
        print('Failed, creating new master pickle')
        print('Creating dataframes from source files')
        dfs = list(map(lambda x: TweetsToDF(pd.read_pickle(x)), in_files))
        master_df = pd.concat(dfs)
        print('Writing master pickle to file')
        with open(MASTER_DF_PATH, 'wb+') as f:
            pickle.dump((len(in_files), master_df), f)
        return master_df

def UpdateTweetDF(in_files, master_df_files, master_df):
    print('Updating with {} new data files'.format(len(in_files)-master_df_files))
    total_files = len(in_files)
    in_files = natsort.natsorted(in_files[master_df_files:], key=lambda y: y.lower())
    dfs = []
    for index, in_file in enumerate(in_files):
        print('Reading file {}'.format(index))
        tweets = pd.read_pickle(in_file)
        dfs.append(TweetsToDF(tweets))
    print('Concatenating files...')
    master_df = pd.concat([master_df] + dfs)
    print('Writing updated master df')
    with open(MASTER_DF_PATH, 'wb+') as f:
        pickle.dump((total_files, master_df), f)
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

