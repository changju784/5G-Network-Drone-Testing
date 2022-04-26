import gmplot
from src.apiKey import *

from src.ml_engines.build_dataset import BuildData


class Map:
    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance

    def visualize(self,dataset):
        total_data = dataset.drop(columns=['id'])
        lat = total_data['latitude'].values.tolist()
        lon = total_data['longitude'].values.tolist()
        center = [sum(lat) / len(lat), sum(lon) / len(lon)]
        gmap3 = gmplot.GoogleMapPlotter(center[0], center[1], 15, apikey=google_api)
        gmap3.scatter(lat, lon, '#000000', size=15, marker=False)
        gmap3.draw("./app/templates/map_history.html")