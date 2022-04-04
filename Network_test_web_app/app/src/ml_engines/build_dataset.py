'''
====================================
 :mod:`build_dataset` {GET data from DB and build a format to training data set}
====================================
'''
import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from src.database import Database



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
        result = Database().get_data()        

        df = pd.DataFrame(result)
        df.columns = ['id', 'download', 'upload', 'latitude', 'longtitude','altitude', 'time_stamp']
        # df.columns = ['id', 'download', 'upload', 'latitude', 'longtitude','altitude']
        return df
