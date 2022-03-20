'''
Data visualization
'''
import pandas as pd
import matplotlib.pyplot as plt
import gmplot

from ml_engines.build_dataset import BuildData

__all__ = ['model_regression']
dataset = BuildData.instance()


class Data:
    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance

    def collected_data(self):
        total_data = dataset.get_data()
        total_data = total_data.drop(columns=['id'])
        lat = total_data['latitude'].values.tolist()
        lon = total_data['longtitude'].values.tolist()
        center = [sum(lat) / len(lat), sum(lon) / len(lon)]
        gmap3 = gmplot.GoogleMapPlotter(center[0], center[1], 15)
        gmap3.scatter(lat, lon, '#FFFFFF', size=15, marker=False)
        gmap3.draw("map11.html")


dd = Data.instance()
print(dd.collected_data())
