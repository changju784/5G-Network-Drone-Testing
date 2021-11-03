'''
====================================
 :mod:`train` {Extract data from DB and conduct pre-processing
Use modeling modules to train data}
====================================
'''

import pandas as pd
import numpy as np
import const.const_path as cpath
from keras_preprocessing import sequence
from sklearn.model_selection import train_test_split

__all__ = ['train']

def multivariate_data(dataset, target, start_idx, end_idx, history_size, target_size, step, single_step=False):
    data = []
    label = []
    start_idx = start_idx + history_size
    if end_idx is None:
        end_idx = len(dataset) - target_size
    for i in range(start_idx, end_idx):
        indices = range(i - history_size, i, step)
        data.append(dataset[indices])
        if single_step:
            label.append(target[i + target_size])
        else:
            label.append(target[i:i+target_size])
    return np.array(data), np.array(label)

def train():
    '''
    :return: keras model
    '''
    # Data preprocessing
    path = cpath.path
    fn = open(path["train_data_path"], 'rt', encoding='ISO-8859-1')
    # total_data = pd.read_excel(fn, index_col=None, header=None, sheet_name='Sheet1')
    total_data = pd.read_csv(fn)
    total_data = total_data.drop(columns=['country', 'country_code', 'date'])
    train_split = len(total_data.index)
    get_download = total_data.drop(columns=['upload_kbps'])
    get_upload = total_data.drop(columns=['download_kbps'])
    get_download = get_download.values
    gd_mean = get_download[:train_split].mean()
    gd_std = get_download[:train_split].std(axis=0)
    get_download = (get_download - gd_mean) / gd_std
    x_train, y_train = multivariate_data(get_download, get_download[:,1], 0, train_split, 720, 72, 6, single_step=True)
    x_val, y_val = multivariate_data(get_download, get_download[:,1], 0, train_split, 720, 72, 6, single_step=True)
    print(x_train.shape)
    # total_data['X'] = total_data.apply(lambda r: [r['total_tests']] + [r['distance_miles']], axis=1)
    # total_data['Y'] = total_data.apply(lambda r: [r['download_kbps']] + [r['upload_kbps']], axis=1)






train()