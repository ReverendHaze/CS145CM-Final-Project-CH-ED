import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA

def GetTrainedModel(data, rank, how):
    if how is 'NMF':
        return NMF(n_components=rank, init='nndsvd', max_iter=200, nls_max_iter=2000, tol=0.0001, sparseness='data', beta=0.4).fit(data)
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

def Sparsity(vec):
    return np.linalg.norm(vec)/np.sum(vec)
