'''
====================================
 :mod:`build_dataset` {GET data from DB and build a format to training data set}
====================================
'''
import os
import pymysql
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
            doc.get('altitude')))
            # doc.get('time_stamp')))

        df = pd.DataFrame(result)
        df.columns = ['id', 'download', 'upload', 'latitude', 'longtitude','altitude']
        return df
