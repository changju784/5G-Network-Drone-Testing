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


def norm(x, t):
    return (x - t['mean']) / t['std']

def train2(prediction):
    path = cpath.path
    fn = open(path["train_data_path"], 'rt', encoding='ISO-8859-1')
    total_data = pd.read_csv(fn)
    total_data = total_data.drop(columns=['country', 'date'])
    total_data['country_code'] = total_data['country_code'].apply(lambda x: ord(x[0]) + ord(x[1]))
    X = total_data[['total_tests', 'distance_miles', 'country_code']]
    y = total_data[['upload_kbps', 'download_kbps']]
    x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)
    x_train, x_test = x_train.to_numpy(), x_test.to_numpy()
    y_train, y_test = y_train.to_numpy(), y_test.to_numpy()
    clf = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(x_train, y_train)
    print(clf.predict([[1666258, 127.944, 168]]))
    print(clf.score(x_test, y_test))

    y_predict = clf.predict(x_test)
    plt.scatter(y_test, y_predict, alpha=0.4)
    plt.xlabel("Actual speed")
    plt.ylabel("Predicted speed")
    plt.title("MULTIPLE LINEAR REGRESSION")
    plt.show()


train2('upload')
