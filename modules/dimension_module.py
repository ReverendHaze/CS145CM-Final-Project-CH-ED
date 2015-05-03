import pandas as pd
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA

def ReduceDimension(data, rank, how, transform=True):
    model = []
    if how is 'NMF':
        model = NMF(n_components=rank, init='nndsvd', sparseness='components')
    elif how is 'PCA':
        model = PCA(n_components=rank, copy=True, whiten=True)

    model.fit(data)
    if transform:
        fitted_data = model.transform(data)
        return (fitted_data, model.reconstruction_err_)
    else:
        return model.reconstruction_err_

