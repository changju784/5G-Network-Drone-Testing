'''
Linear regression
'''

import const.const_path as cpath
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


def norm(x, t):
    return (x - t['mean']) / t['std']

def train2(prediction):
    path = cpath.path
    fn = open(path["train_data_path"], 'rt', encoding='ISO-8859-1')
    total_data = pd.read_csv(fn)
    # total_data = total_data.drop(columns=['country', 'country_code', 'date'])
    total_data = total_data.drop(columns=['country', 'date'])
    total_data['country_code'] = total_data['country_code'].apply(lambda x: ord(x[0]) + ord(x[1]) )
    X = total_data[['total_tests', 'distance_miles', 'country_code']]
    y = total_data[['upload_kbps', 'download_kbps']]
    X_stat, y_stat = X.describe(), y.describe()
    X_stat, y_stat = X_stat.transpose(), y_stat.transpose()
    X_norm = norm(X, X_stat)
    y_norm = norm(y, y_stat)
    x_train, x_test, y_train, y_test = train_test_split(X_norm, y_norm, train_size=0.8, test_size=0.2)
    mlr = LinearRegression()
    mlr.fit(x_train, y_train)
    sample_input = [[1666258, 127.944, 168]]
    sample_test = mlr.predict(sample_input)
    print(sample_test)


    y_predict = mlr.predict(x_test)
    plt.scatter(y_test, y_predict, alpha=0.4)
    plt.xlabel("Actual Rent")
    plt.ylabel("Predicted Rent")
    plt.title("MULTIPLE LINEAR REGRESSION")
    print(mlr.score(x_train, y_train))





train2('upload')