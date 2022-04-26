'''
====================================
 :mod:`build_dataset` {GET data from DB and build a format to training data set}
====================================
'''
import os
import pandas as pd
import firebase_admin
import geopy
from firebase_admin import credentials
from firebase_admin import firestore
from src.database import Database



__all__ = ['build_dataset']
db = firestore.client()

class BuildData:

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance

    def __init__(self):
        self.geolocator = geopy.Nominatim(user_agent="5G_Network_Test")
        self.data = None

    def get_zipcode(self, lat, lon):
        try:
            location = self.geolocator.reverse((lat, lon))
            return location.raw['address']['postcode']
        except (AttributeError, KeyError, ValueError):
            return 0

    def get_data(self):
        db = Database()
        result = db.get_data()  

        df = pd.DataFrame(result)
        df.columns = ['id', 'download', 'upload', 'latitude', 'longitude', 'altitude', 'time_stamp','zipcode']
        zipcodes = []
        for idx, row in df.iterrows():
            if row['zipcode'] == "":
                try:
                    zipcode = self.get_zipcode(row['latitude'], row['longitude'])
                except:
                    zipcode = "0"

                zipcodes.append(zipcode)
                db.set_zipcode(row['id'],zipcode)
            else:
                zipcodes.append(row['zipcode'])
        

        df['zipcode'] = zipcodes
        self.data = df
        df.to_csv('./app/src/ml_engines/dataset/collected_data.csv', index=False)
        return df


