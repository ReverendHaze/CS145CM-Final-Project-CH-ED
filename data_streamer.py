#! /bin/python

#Import the necessary methods and libraries
import json
import pandas as pd
import datetime
import pickle
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

RESULTS_FOLDER = 'out'

#All boxes are of the form W:S:E:N with all values given in
#longitude/latitude. Boxes returned from the google maps API.
CHICAGO_BOX = [ -87.94, 41.64,  -87.52, 42.02]
LA_BOX      = [-118.67, 33.70, -118.16, 34.34]
HOUSTON_BOX = [ -95.79, 29.52,  -95.01, 30.11]

WINDOW_LENGTH_IN_SEC = 600 #Seconds in a storage window

#This is a basic listener that just prints received tweets to stdout.
class TweetListener(StreamListener):
    ts = 0
    tweets = []

    def __init__(self):
        self.ts = datetime.datetime.now()

    def on_data(self, data):
        t_diff = datetime.datetime.now() - self.ts
        if(t_diff.total_seconds() > WINDOW_LENGTH_IN_SEC):
            ts_string = self.ts.strftime('%d_%m_%y_%H_%M')
            print('Finished period {}'.format(ts_string))
            with open('{}/{}.pickle'.format(RESULTS_FOLDER, ts_string), "wb+") as f:
                pickle.dump(self.tweets, f)
            self.tweets = []
            self.ts = datetime.datetime.now()

        tweet = json.loads(data)
        self.tweets.append(tweet)
        return True

    def on_error(self, status):
        print(status)

def TweetsToDF(tweets):
    tweets_dict = {}
    tweets_dict['text'] = map(lambda x: x['text'], tweets)
    tweets_dict['id_num'] = map(lambda x: x['id'], tweets)
    tweets_dict['hashtags'] = map(lambda x: ','.join(x['entities']['hashtags']), tweets)
    tweets_dict['mentions'] = map(lambda x: ','.join(x['entities']['user_mentions']), tweets)
    tweets_dict['retweeted'] = map(lambda x: x['retweeted'], tweets)
    tweets_dict['coords'] = map(lambda x: x['coordinates'], tweets)
    tweets_dict['u_id'] = map(lambda x: x['user']['id'], tweets)
    tweets_dict['u_follow'] = map(lambda x: x['user']['followers_count'], tweets)
    tweets_dict['u_stat'] = map(lambda x: x['user']['statuses_count'], tweets)
    tweets_dict['u_friends'] = map(lambda x: x['user']['friends_count'], tweets)
    tweets_dict['u_lang'] = map(lambda x: x['user']['lang'], tweets)
    tweets_dict['geo'] = map(lambda x: x['geo'], tweets)
    tweets_dict['place'] = map(lambda x: x['place'], tweets)
    return pd.DataFrame(tweets_dict)


if __name__ == '__main__':
#This handles Twitter authetification and the connection to Twitter Streaming API
    listener = TweetListener()
    auth_dict = pickle.load('credentials.pickle')
    auth = OAuthHandler(auth_dict['consumer_key'], auth_dict['consumer_secret'])
    auth.set_access_token(auth_dict['access_token'], auth_dict['access_token_secret'])
    stream = Stream(auth = auth, listener = listener)
    stream.filter(locations=CHICAGO_BOX+LA_BOX+HOUSTON_BOX)

