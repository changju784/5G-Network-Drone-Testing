from distutils.command.upload import upload
import threading
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os


class Database():

    data = os.path.abspath(os.path.dirname(__file__)) + "/serviceAccountKey.json"
    cred = credentials.Certificate(data)
    firebase_admin.initialize_app(cred)

    
    def __init__(self):
        self.db = firestore.client()
        self.callback_done = threading.Event()
        self.upload = 0.0
        self.download = 0.0
        self.altitude = 0.0
        self.longitude = 0.0
        self.latitude = 0.0
        self.zipcode = ""
    
    def set_true(self):
        self.db.collection('operations').document('operate').set({'test': True})

    def set_false(self):
        self.db.collection('operations').document('operate').set({'test':False})

    def set_zipcode(self, id, zipcode):
        self.db.collection('data').document(id).update({'zipcode':zipcode})

    def save_model(self,df):
        self.db.collection('model').document('mlmodel').set({'test':False})

    def on_snapshot(self,doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            self.upload = doc.get("upload")
            self.download = doc.get("download")
            self.longitude = doc.get("longitude")
            self.latitude = doc.get("latitude")
            self.altitude = doc.get("altitude")
            self.zipcode = doc.get("zipcode")
        self.callback_done.set()
    
    def get_data(self):
        result = []
        docs = self.db.collection('data').stream()

        for doc in docs:
            result.append(
            (doc.id, \
            doc.get('download'), \
            doc.get('upload'), \
            doc.get('latitude'), \
            doc.get('longitude'), \
            doc.get('altitude'), \
            doc.get('time_stamp'), \
            doc.get('zipcode')
            ))
            
        return result


        
