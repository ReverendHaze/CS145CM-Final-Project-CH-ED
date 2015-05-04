import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA

def GetTrainedModel(data, rank, how):
    if how is 'NMF':
        return NMF(n_components=rank, init='nndsvd', max_iter=200, nls_max_iter=2000, tol=0.0001, sparseness='components').fit(data)
    elif how is 'PCA':
        return PCA(n_components=rank, copy=True, whiten=True).fit(data)

def TransformData(data, trained_model):
    data = list(map(lambda x: np.transpose(data[:,x]), range(data.shape[1])))
    return model.transform(data)

def GetReductionErrors(trained_model, original, samples):
    components = trained_model.components_
    print(type(components))
    print(components.size)
    #return trained_model.reconstruction_err_


