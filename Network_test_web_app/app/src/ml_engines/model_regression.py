'''
Linear regression
'''
import joblib
from sklearn.datasets import make_regression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
# import matplotlib.pyplot as plt
from src.ml_engines.build_dataset import BuildData
from src.map import Map

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

__all__ = ['model_regression']

dataset = BuildData.instance()
map = Map.instance()

class Modeling:
    def __init__(self):
        try:
            self.clf = joblib.load("./app/src/ml_engines/model/model.pkl")
        except:
            self.clf = None
        fn = open("./app/src/ml_engines/dataset/collected_data.csv", 'rt', encoding='ISO-8859-1')
        self.df = pd.read_csv(fn)


    def data_analysis(self):
        total_data = self.df
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
    
    def load_latest_model(self):

        df = self.df.copy()
        df = self.preprocess(df)
        X = df[['longitude', 'latitude', 'altitude']]
        y = df[['upload', 'download']]
        x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)
        x_train, x_test = x_train.to_numpy(), x_test.to_numpy()
        y_train, y_test = y_train.to_numpy(), y_test.to_numpy()

        # Multi-out regression model
        accuracy = self.clf.score(x_test, y_test)
        map.visualize(df)
        self.visualize(df)



        return round(accuracy, 2) * 100


    
    def preprocess(self,df):
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
        return df

    def train(self):
        self.df = dataset.get_data()

        # df = self.df.copy()
        df = self.df.copy()
        map.visualize(df)

        df = self.preprocess(df)

        X = df[['longitude', 'latitude', 'altitude']]
        y = df[['upload', 'download']]
        x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)
        x_train, x_test = x_train.to_numpy(), x_test.to_numpy()
        y_train, y_test = y_train.to_numpy(), y_test.to_numpy()

        # Multi-out regression model
        self.clf = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(x_train, y_train)

        accuracy = self.clf.score(x_test, y_test)

        joblib.dump(self.clf,"./app/src/ml_engines/model/model.pkl")
        
        self.visualize(df)



        return round(accuracy, 2) * 100


    def predict(self, lon,lat,alt):
        # print(self.clf.predict[[lon,lat,alt]])
        # print(self.clf)
        prediction = self.clf.predict([[lon, lat , alt]])
        return [str(round(prediction[0][0],2)), str(round(prediction[0][1],2))]
    
    def visualize(self,reshaped_df):
        # 3D plot
        df = reshaped_df
        X = df[['zipcode', 'altitude']].values.reshape(-1, 2)
        Y = df[['upload']]
        Regressor = LinearRegression()
        Regressor.fit(X, Y)
        x_surf, y_surf = np.meshgrid(np.linspace(df.zipcode.min(), df.zipcode.max(), 100),
                                     np.linspace(df.altitude.min(), df.altitude.max(), 100))
        onlyX = pd.DataFrame({'zipcode': x_surf.ravel(), 'altitude': y_surf.ravel()})
        fittedY = Regressor.predict(onlyX)
        fittedY = np.array(fittedY)
        plt.switch_backend('Agg') 
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df['zipcode'], df['altitude'], df['upload'], c='red', marker='o', alpha=0.5)
        ax.plot_surface(x_surf, y_surf, fittedY.reshape(x_surf.shape), color='b', alpha=0.3)
        ax.set_xlabel('Zipcode')
        ax.set_ylabel('Altitude')
        ax.set_zlabel('Upload Speed')
        plt.title("3D graph of upload speed prediction model")
        plt.savefig("./app/src/ml_engines/model/output.jpg")



