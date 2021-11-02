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



def train():
    '''
    :return: keras model
    '''
    # Data preprocessing
    path = cpath.path
    fn = open(path["train_data_path"], 'rt', encoding='ISO-8859-1')
    # total_data = pd.read_excel(fn, index_col=None, header=None, sheet_name='Sheet1')
    total_data = pd.read_csv(fn)
    print(total_data)


train()