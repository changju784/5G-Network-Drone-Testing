'''
====================================
 :mod:`build_dataset` {GET data from DB and build a format to training data set}
====================================
'''
import os
import geopy
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

data = os.path.abspath(os.path.dirname(__file__)) + "/serviceAccountKey.json"
cred = credentials.Certificate(data)
firebase_admin.initialize_app(cred)

db = firestore.client()

__all__ = ['build_dataset']

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

    def get_zipcode(self, lat, lon):
        try:
            location = self.geolocator.reverse((lat, lon))
            return location.raw['address']['postcode']
        except (AttributeError, KeyError, ValueError):
            return 0

    def get_data(self):
        result = []
        docs = db.collection('data').stream()

        for doc in docs:
            result.append(
            (doc.id, \
            doc.get('download'), \
            doc.get('upload'), \
            doc.get('latitude'), \
            doc.get('longitude'), \
            doc.get('altitude'), \
            doc.get('time_stamp')))

        df = pd.DataFrame(result)
        df.columns = ['id', 'download', 'upload', 'latitude', 'longtitude', 'altitude', 'time_stamp']
        print(df.head())
        # # Add time stamp parameter
        # new_ts = []
        # for ts in df['time_stamp']:
        #     ts_split = ts.split(' ')
        #     date = ts_split[1].split(':')
        #     if 5 < int(date[0]) or 18  < int(date[0]):
        #         df.replace(ts, "DAY")
        #         new_ts.append("DAY")
        #     else:
        #         df.replace(ts, "NIGHT")
        #         new_ts.append("NIGHT")
        # df.loc[:, 'time_stamp'] = new_ts

        # Add zipcode parameter
        zipcodes = []
        for idx, row in df.iterrows():
            try:
                print(self.get_zipcode(row['latitude'], row['longtitude']))
                zipcodes.append(self.get_zipcode(row['latitude'], row['longtitude']))
            except:
                zipcodes.append(0)
            if idx % 100 == 0:
                print(idx, " zipcodes converted out of ", len(df.index))
        df['zipcode'] = zipcodes
        print('process ended')
        df.to_csv('../ml_engines/dataset/collected_data.csv', index=False)
