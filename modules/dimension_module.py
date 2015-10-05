import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import random

def GetTrainedModel(data, rank, how, config):
    if how is 'NMF':
        print(config)
        return NMF(n_components=rank, init='nndsvd', max_iter=500, nls_max_iter=500, tol=0.01, sparseness=config['SPARSENESS'], beta=config['BETA']).fit(data)
    elif how is 'PCA':
        return PCA(n_components=rank, copy=True, whiten=True).fit(data)

def TransformData(data, trained_model):
    data = list(map(lambda x: np.transpose(data[:,x]), range(data.shape[1])))
    return trained_model.transform(data)

def GetTopics(trained_model, ng_per_topic, name_list):
    res = {}
    for index, topic in enumerate(trained_model.components_):
        topic_indices = topic.argsort()[:-ng_per_topic-1:-1]
        res[index] = (np.around(Sparsity(topic), decimals=2), list(map(lambda x: name_list[x], topic_indices)))
    return res

def GetAreaPlot(trained_model, city):
    fig = plt.figure(figsize=(11.5, 8.0))
    ax = fig.add_subplot(111)
    #ax.set_color_cycle()

    running_sum = trained_model.components_[0]
    x = np.arange(len(running_sum))
    ax.fill_between(x, running_sum)
    for index, topic in enumerate(trained_model.components_[1:]):
        ax.fill_between(x, running_sum, running_sum+topic, facecolor=plt.cm.cool(index))
        running_sum += topic
    plt.savefig('out/graph/area_{}.png'.format(city))


def GetRandHex():
    while True:
        r = lambda: random.randint(0,255)
        yield ('#%02X%02X%02X' % (r(),r(),r()))

def Sparsity(vec):
    return np.linalg.norm(vec)/np.sum(vec)
