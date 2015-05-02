import pandas as pd
from sklearn.decomposition import NMF

n_topics = 50 
n_top_words = 20

in_file = 

hist = pd.pickle.io.read_pickle(in_file)

nmf = NMF(n_components=n_topics, random_state=1).fit(hist)

feature_names = hist.columns

for topic_idx, topic in enumerate(nmf.components_):
    print("Topic #%d:" % topic_idx)
    print(" ".join([feature_names[i]
                    for i in topic.argsort()[:-n_top_words - 1: -1]]))
    print()


