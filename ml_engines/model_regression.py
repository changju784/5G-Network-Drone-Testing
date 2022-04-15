'''
Linear regression
'''
## Const ##
from collections import Counter
import time
import numpy as np
from sklearn.linear_model import LinearRegression

import const.const_path as cpath
import pandas as pd
import matplotlib.pyplot as plt
from ml_engines.build_dataset import BuildData
import geopy
import pandas as pd
## Modeling ##
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
## Plots ##
from sklearn import linear_model
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
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
        self.geolocator = geopy.Nominatim(user_agent="5G_Network_Test")

    def data_analysis(self):
        path = cpath.path['train_data_path2']
        # total_data = dataset.get_data()
        fn = open(path, 'rt', encoding='ISO-8859-1')
        total_data = pd.read_csv(fn)
        # total_data = total_data.drop(columns=['id'])
        new_ts = []
        for ts in total_data['time_stamp']:
            ts_split = ts.split(' ')
            date = ts_split[1].split(':')
            if 5 < int(date[0]) or 18  < int(date[0]):
                total_data.replace(ts, "DAY")
                new_ts.append("DAY")
            else:
                total_data.replace(ts, "NIGHT")
                new_ts.append("NIGHT")
        total_data.loc[:, 'time_stamp'] = new_ts
        print("Total network speed test conducted: ", len(total_data.index))
        print("Average altitudes(ft): ", round(total_data['altitude'].mean(), 4))
        print("Average upload speed(Mbps): ", round(total_data['upload'].mean() / 1000, 4))
        print("Average download speed(Mbps): ", round(total_data['download'].mean() / 1000, 4))

        # Group by altitudes
        # total_data.plot(kind='scatter', y = 'upload', x = 'altitude')
        # plt.title("upload speed vs altitudes")
        # plt.xlabel("Altitudes")
        # plt.ylabel("Upload Speed")
        # plt.show()
        # uploads_ = total_data.groupby('altitude')['upload'].apply(list)
        # for altitude, upload in uploads_.items():
        #     uploads_[altitude] = sum(upload) / len(upload)
        # uploads_.plot(style='.')
        # plt.show()
        # for i, u in enumerate(uploads_):
        #     uploads_[i] = sum(u) / len(u)

    def get_zipcode(self, lat, lon):
        try:
            location = self.geolocator.reverse((lat, lon))
            return location.raw['address']['postcode']
        except (AttributeError, KeyError, ValueError):
            return 0

    def train(self):
        # Get dataset
        path = cpath.path['train_data_path']
        fn = open(path, 'rt', encoding='ISO-8859-1')
        df = pd.read_csv(fn)
        df = df.drop(columns=['id', 'time_stamp'])

        # Data pre-processing
        df.dropna()
        df['upload'] /= 1000
        df['download'] /= 1000
        df = df[(df['upload'] > 25) & (df['download'] > 25) & (df['altitude'] > -50) & (df['zipcode'] != '0')] # Drop unnecessary data
        indexes = df[(df['upload'] < 40) & (df['download'] < 50) & (df['altitude'] < 50)].index
        df.drop(indexes, inplace=True)

        for index, row in df.iterrows():
            zipcode = row['zipcode'][:5]
            if len(row['zipcode']) > 5:
                df.loc[index,'zipcode'] = zipcode
            df.loc[index, 'zipcode'] = int(zipcode)
        zipcodes = set(df['zipcode'].tolist())
        zipcodes = sorted(zipcodes)
        dflist = [df[df['zipcode'] == zipcode] for zipcode in zipcodes]
        for df in dflist:
            grouped_by_alt = df.groupby(pd.cut(df["altitude"], np.arange(-50, 250, 50))).mean() # Group altitude in range [-50~0, 0~50, 50~100, 100~150, 150~200]
            avg_uploads = grouped_by_alt['upload'].tolist()
            avg_downloads = grouped_by_alt['download'].tolist()
            for index, row in df.iterrows():
                altitude = row['altitude']
                if -50 < altitude <= 0:
                    df.loc[index, 'upload'] = avg_uploads[0]
                    df.loc[index, 'download'] = avg_downloads[0]
                elif 0 < altitude <= 50:
                    df.loc[index, 'upload'] = avg_uploads[1]
                    df.loc[index, 'download'] = avg_downloads[1]
                elif 50 < altitude <= 100:
                    df.loc[index, 'upload'] = avg_uploads[2]
                    df.loc[index, 'download'] = avg_downloads[2]
                elif 100 < altitude <= 150:
                    df.loc[index, 'upload'] = avg_uploads[3]
                    df.loc[index, 'download'] = avg_downloads[3]
                elif 150 < altitude <= 200:
                    df.loc[index, 'upload'] = avg_uploads[4]
                    df.loc[index, 'download'] = avg_downloads[4]
        df = pd.concat(dflist)

        X = df[['longtitude', 'latitude', 'altitude']]
        y = df[['upload', 'download']]
        x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)
        x_train, x_test = x_train.to_numpy(), x_test.to_numpy()
        y_train, y_test = y_train.to_numpy(), y_test.to_numpy()

        # Multi-out regression model
        self.clf = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(x_train, y_train)

        # sample_predict = self.clf.predict([[42.350872, -71.125286, -8.944273]]) # upload: 30298 download: 54478
        # print("Sample predicdtion for latitude: ", 42.350872, " lontitude: ", -71.125286, " altitude: ", -8.944273)
        # print("Actual Upload speed(Mbps): ", 42, "Download speed(Mbps): ", 54)
        # print("Predicted Upload speed: ", round(sample_predict[0][0], 2), "Predicted Download speed: ", round(sample_predict[0][1], 2))
        accuracy = self.clf.score(x_test, y_test)
        # print('\n')
        # print("Model Acurracy: ", round(accuracy, 2))
        # #
        # y_predict = self.clf.predict(x_test)
        # plt.scatter(y_test, y_predict, alpha=0.4, label="Model Accuracy:%.2f" % accuracy)
        # plt.xlabel("Actual speed")
        # plt.ylabel("Predicted speed")
        # plt.title("MULTIPLE LINEAR REGRESSION")
        # plt.legend()
        # plt.show()
        #
        # ypred = self.clf.predict(x_test)
        # print("Upload Speed MSE:%.4f" % mean_squared_error(y_test[:, 0], ypred[:, 0]))
        # print("Download Speed MSE:%.4f" % mean_squared_error(y_test[:, 1], ypred[:, 1]))
        # #
        # x_ax = range(len(x_test))
        # plt.plot(x_ax, y_test[:, 0], label="Actual Upload Speed", color='c')
        # plt.plot(x_ax, ypred[:, 0], label="Predicted Upload Speed", color='b')
        # plt.plot(x_ax, y_test[:, 1], label="Actual Download Speed", color='m')
        # plt.plot(x_ax, ypred[:, 1], label="Predicted Download Speed", color='r')
        # plt.legend()
        # plt.show()

        # 3D plot
        X = df[['zipcode', 'altitude']].values.reshape(-1, 2)
        Y = df[['upload']]
        Regressor = LinearRegression()
        Regressor.fit(X, Y)
        x_surf, y_surf = np.meshgrid(np.linspace(df.zipcode.min(), df.zipcode.max(), 100),
                                     np.linspace(df.altitude.min(), df.altitude.max(), 100))
        onlyX = pd.DataFrame({'zipcode': x_surf.ravel(), 'altitude': y_surf.ravel()})
        fittedY = Regressor.predict(onlyX)
        fittedY = np.array(fittedY)
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df['zipcode'], df['altitude'], df['upload'], c='red', marker='o', alpha=0.5)
        ax.plot_surface(x_surf, y_surf, fittedY.reshape(x_surf.shape), color='b', alpha=0.3)
        ax.set_xlabel('Zipcode')
        ax.set_ylabel('Altitude')
        ax.set_zlabel('Upload Speed')
        plt.title("3D graph of upload speed prediction model")
        plt.show()

        return round(accuracy, 2) * 100

    def predict(self, lon,lat,alt,time):
        # print(self.clf.predict[[lon,lat,alt]])
        # print(self.clf)
        prediction = self.clf.predict([[lon, lat , alt, time]])
        return [str(prediction[0][0]), str(prediction[0][1])]


