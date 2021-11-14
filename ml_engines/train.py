'''
====================================
 :mod:`train` {Extract data from DB and conduct pre-processing
Use modeling modules to train data}
====================================
'''

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
# import const.const_path as cpath
import seaborn as sns
from keras_preprocessing import sequence
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import build_model as build_model

__all__ = ['train']

def norm(x, t):
        return (x - t['mean']) / t['std']

def train():
    '''
    :return: keras model
    '''
    # Data preprocessing
    # path = cpath.path
    path = "dataset/sample_train_data.csv"
    fn = open(path, 'rt', encoding='ISO-8859-1')
    total_data = pd.read_csv(fn)

    # if prediction == "download":
    #     total_data = total_data.drop(columns=['country', 'date', 'upload_kbps'])
    # else:
    #     total_data = total_data.drop(columns=['country', 'date', 'download_kbps'])

    total_data = total_data.drop(columns=['country', 'date'])
    total_data['country_code'] = total_data['country_code'].apply(lambda x: ord(x[0]) + ord(x[1]))


    # Train Test split
    train_dataset = total_data.sample(frac=0.8, random_state=0)
    test_dataset = total_data.drop(train_dataset.index)


    train_labels = pd.concat([train_dataset.pop(x) for x in['upload_kbps','download_kbps']], axis = 1)
    test_labels = pd.concat([test_dataset.pop(x) for x in['upload_kbps','download_kbps']], axis = 1)
    print(train_labels)
    

    # train_dataset = train_dataset.drop(columns=['download_kbps' , 'upload_kbps'])
    # test_dataset = test_dataset.drop(columns=['download_kbps' , 'upload_kbps'])
    

    # sns.pairplot(train_dataset[["download_kbps", "upload_kbps", "total_tests", "distance_miles"]], diag_kind="kde")
    # plt.show()

    train_stats = train_dataset.describe()
    # if prediction == "download":
    #     train_stats.pop("download_kbps")
    #     train_labels = train_dataset.pop('download_kbps')
    #     test_labels = test_dataset.pop('download_kbps')
    # elif prediction == "upload":
    #     train_stats.pop("upload_kbps")
    #     train_labels = train_dataset.pop('upload_kbps')
    #     test_labels = test_dataset.pop('upload_kbps')
    train_stats = train_stats.transpose()

    normed_train_data = norm(train_dataset, train_stats)
    normed_test_data = norm(test_dataset, train_stats)
    train_len = len(train_dataset.keys())

    # Model Training
    model = build_model.model_regression(normed_train_data, train_labels, train_len)
    loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
    print(model.predict( [[1666258, 127.944, 168]] ))
    
    print("average error rate of testset: {:5.2f}".format(mae))


train()