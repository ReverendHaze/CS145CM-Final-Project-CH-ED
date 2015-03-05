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

if __name__ == '__main__':
#This handles Twitter authetification and the connection to Twitter Streaming API
    listener = TweetListener()
    with open('credentials.pickle', 'rb') as f:
        auth_dict = pickle.load(f)
    auth = OAuthHandler(auth_dict['consumer_key'], auth_dict['consumer_secret'])
    auth.set_access_token(auth_dict['access_token'], auth_dict['access_token_secret'])
    stream = Stream(auth = auth, listener = listener)
    stream.filter(locations=CHICAGO_BOX+LA_BOX+HOUSTON_BOX)

