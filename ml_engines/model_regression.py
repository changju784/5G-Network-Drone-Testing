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

    def __init__(self):
        self.clf = None

    def data_analysis(self):
        path = cpath.path['train_data_path']
        # total_data = dataset.get_data()
        fn = open(path, 'rt', encoding='ISO-8859-1')
        total_data = pd.read_csv(fn)
        total_data = total_data.drop(columns=['id', 'time_stamp'])
        print("Total network speed test conducted: ", len(total_data.index))
        print("Average altitudes(ft): ", round(total_data['altitude'].mean(), 4))
        print("Average upload speed(Mbps): ", round(total_data['upload'].mean() / 1000, 4))
        print("Average download speed(Mbps): ", round(total_data['download'].mean() / 1000, 4))

        # Group by same spots
        # total_data['GPS'] = list(zip(total_data['latitude'], total_data['longtitude']))
        # altitudes = total_data.groupby('GPS')['altitude'].apply(list)
        # print(altitudes)
        # same_spot = total_data.loc[total_data['GPS'] == (42.3560934, -71.1212706)]
        # same_spot.plot(kind='scatter', y = 'upload', x = 'altitude')
        # plt.title("Upload speed at 42.3560934, -71.1212706")
        # plt.show()

        # Group by altitudes
        # total_data.plot(kind='scatter', y = 'download', x = 'altitude')
        # plt.title("download speed vs altitudes")
        # plt.show()
        # uploads_ = total_data.groupby('altitude')['upload'].apply(list)
        # for altitude, upload in uploads_.items():
        #     uploads_[altitude] = sum(upload) / len(upload)
        # uploads_.plot(style='.')
        # plt.show()
        # for i, u in enumerate(uploads_):
        #     uploads_[i] = sum(u) / len(u)




    def train(self):
        # Get dataset
        path = cpath.path['train_data_path']
        fn = open(path, 'rt', encoding='ISO-8859-1')
        df = pd.read_csv(fn)
        df = df.drop(columns=['id', 'time_stamp'])

        # Data pre-processing
        df.dropna()
        df = df[(df['upload'] > 0) & (df['download'] > 0)]


        # X = df[['latitude', 'longtitude', 'altitude']]
        # y = df[['upload', 'download']]
        # x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)
        # x_train, x_test = x_train.to_numpy(), x_test.to_numpy()
        # y_train, y_test = y_train.to_numpy(), y_test.to_numpy()
        # self.clf = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(x_train, y_train)

        # sample_predict = self.clf.predict([[42.350872, -71.125286, -8.944273]]) # upload: 30298 download: 54478
        # print("Sample predicdtion for latitude: ", 42.350872, " longtitude: ", -71.125286, " altitude: ", -8.944273)
        # print("Upload speed: ", round(sample_predict[0][0], 2), "Download speed: ", round(sample_predict[0][1], 2))
        #
        # accuracy = self.clf.score(x_test, y_test)
        # print("Model Acurracy: ", round(accuracy, 2))

        # y_predict = self.clf.predict(x_test)
        # return round(accuracy,2) * 100
        # plt.scatter(y_test, y_predict, alpha=0.4, label="Model Accuracy:%.2f" % accuracy)
        # plt.xlabel("Actual speed")
        # plt.ylabel("Predicted speed")
        # plt.title("MULTIPLE LINEAR REGRESSION")
        # plt.legend()
        # plt.show()

    def predict(self, lon,lat,alt):
        # print(self.clf.predict[[lon,lat,alt]])
        # print(self.clf)
        prediction = self.clf.predict([[lon, lat , alt]])
        return [str(prediction[0][0]), str(prediction[0][1])]

