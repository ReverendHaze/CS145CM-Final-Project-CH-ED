import pandas as pd
import pickle
import collections
import ark_tweet_nlp_python.CMUTweetTagger as CMUTweetTagger

in_file = 'out/master.pickle'

#print(count_pos)
#print(all_unique_pos)
#
#print(count_pos)
#print(all_unique_pos)

def pos_tag(tweet_series):
    tagged = CMUTweetTagger.runtagger_parse(list_of_tweets, run_tagger_cmd="java -XX:ParallelGCThreads=2 -Xmx500m -jar ark-tweet-nlp-0.3.2/ark-tweet-nlp-0.3.2.jar")
    return(tagged)

def get_pos(tagged_tweet):
    pos = zip(*tagged_tweet)[1]
    unique_pos = set(pos)
    return pos, unique_pos

def build_histogram(token_list, columns):
    hist_list = list(map(lambda x: get_counts(x, columns), token_list))
    return pd.DataFrame(hist_list, columns=columns)

def get_counts(tokens, columns):
    counter = Counter(tokens)
    return list(map(lambda x: counter[x], columns))

tweet_df = pd.io.pickle.read_pickle(in_file)

tagged = pos_tag(tweet_df.text)

all_pos, all_unique_pos = map(get_pos, tagged)
all_unique_pos = list(reduce(set.union, all_unique_pos)

hist_columns = build_histogram(all_pos, all_unique_pos)
hist_columns['id'] = tweet.id


with open('pos_df.pickle', 'w+') as f:
    pickle.dump(hist_columns, f)

