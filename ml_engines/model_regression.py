'''
Linear regression
'''
from sklearn.datasets import make_regression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
import numpy as np
import const.const_path as cpath
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
import matplotlib.pyplot as plt
from ml_engines.build_dataset import BuildData

__all__ = ['model_regression']
dataset = BuildData.instance()

class Modeling:
    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance

    def train(self):
        total_data = dataset.get_data()
        total_data = total_data.drop(columns=['id'])
        X = total_data[['latitude', 'longtitude', 'altitude']]
        y = total_data[['upload', 'download']]
        
        x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)
        x_train, x_test = x_train.to_numpy(), x_test.to_numpy()
        y_train, y_test = y_train.to_numpy(), y_test.to_numpy()
        clf = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(x_train, y_train)
        sample_predict = clf.predict([[42.350872, -71.125286, -8.944273]]) # upload: 30298 download: 54478
        print("Sample predicdtion for latitude: ", 42.350872, " longtitude: ", -71.125286, " altitude: ", -8.944273)
        print("Upload speed: ", round(sample_predict[0][0], 2), "Download speed: ", round(sample_predict[0][1], 2))
        accuracy = clf.score(x_test, y_test)
        print("Model Acurracy: ", round(accuracy, 2))

        y_predict = clf.predict(x_test)
        plt.scatter(y_test, y_predict, alpha=0.4, label="Model Accuracy:%.2f" % accuracy)
        plt.xlabel("Actual speed")
        plt.ylabel("Predicted speed")
        plt.title("MULTIPLE LINEAR REGRESSION")
        plt.legend()
        plt.show()


