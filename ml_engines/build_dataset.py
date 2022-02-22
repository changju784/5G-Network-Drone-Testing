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
def get_data():

    result = []
    docs = db.collection('data').stream()

    for doc in docs:
#        print(doc.get('download'))
        result.append(
        (doc.id, \
        doc.get('download'), \
        doc.get('upload'), \
        doc.get('latitude'), \
        doc.get('longitude'), \
        doc.get('altitude') ))

    df = pd.DataFrame(result)
    df.columns = ['id', 'download', 'upload', 'latitude', 'longtitude','altitude']

    return df

