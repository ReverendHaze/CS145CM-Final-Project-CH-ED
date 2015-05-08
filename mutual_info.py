import pandas as pd
import pickle
import glob
from sklearn.metrics import mutual_info_score

# mi_calc takes in the name of a subfolder of the current directory
# and outputs a text file wherein each line te

def mi_calc(in_fold):
    out_file= 'mutual_information.txt'

    mi_dict={}

    for file in glob.glob(in_fold):
        matrix = pd.io.pickle.read_pickle(file)
        for col in list(matrix.columns):
            mi = mutual_info_score(matrix[bigram_col], matrix[positive_col])
            mi_dict[col] = mi

    with open(out_file, 'wb+') as f:
        pickle.dump(mi_dict,f)


