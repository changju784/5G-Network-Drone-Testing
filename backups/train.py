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
import ml_engines.build_model as build_model
from tensorflow.keras.models import load_model

__all__ = ['train']

def norm(x, t):
        return (x - t['mean']) / t['std']

def train():
    '''
    :return: keras model
    '''
    # Data preprocessing
    # path = cpath.path
    path = "../ml_engines/dataset/sample_train_data.csv"
    fn = open(path, 'rt', encoding='ISO-8859-1')
    total_data = pd.read_csv(fn)
    total_data = total_data.drop(columns=['country', 'country_code', 'date'])
    print(total_data)
    # if prediction == "download":
    #     total_data = total_data.drop(columns=['country', 'country_code', 'date', 'upload_kbps'])
    # else:
    #     total_data = total_data.drop(columns=['country', 'country_code', 'date', 'download_kbps'])

    # Train Test split
    train_dataset = total_data.sample(frac=0.8, random_state=0)
    test_dataset = total_data.drop(train_dataset.index)
    sns.pairplot(train_dataset[["download_kbps", "upload_kbps", "total_tests", "distance_miles"]], diag_kind="kde")
    plt.show()
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
    model = build_model.model_regression(train_dataset, train_labels, train_len, prediction)
    loss, mae, mse = model.evaluate(test_dataset, test_labels, verbose=2)
    print("average error rate of testset: {:5.2f}".format(mae))
    example_batch = test_dataset[:10]
    print(example_batch)
    example_result = model.predict(example_batch)
    print(example_result)


def predict(data, predict):
    path = cpath.path
    if predict == 'upload':
        loaded_model = load_model(path["upload_model_path"])
    else:
        loaded_model = load_model(path["download_model_path"])

    pred_result = loaded_model.predict(data).flatten()
    return pred_result








    # def bm():
    #     model = keras.Sequential([
    #         layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
    #         layers.Dense(64, activation='relu'),
    #         layers.Dense(1)
    #     ])
    #
    #     optimizer = tf.keras.optimizers.RMSprop(0.001)
    #
    #     model.compile(loss='mse',
    #                   optimizer=optimizer,
    #                   metrics=['mae', 'mse'])
    #     return model
    #
    # # example_batch = normed_train_data[:10]
    # # example_result = model.predict(example_batch)
    #
    # class PrintDot(keras.callbacks.Callback):
    #     def on_epoch_end(self, epoch, logs):
    #         if epoch % 100 == 0: print('')
    #         print('.', end='')
    #
    # EPOCHS = 20
    #
    # model = bm()
    #
    # early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
    #
    # history = model.fit(normed_train_data, train_labels, epochs=EPOCHS,
    #                     validation_split=0.2, verbose=0, callbacks=[early_stop, PrintDot()])
    #
    # loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
    #
    # print("테스트 세트의 평균 절대 오차: {:5.2f} MPG".format(mae))


train()