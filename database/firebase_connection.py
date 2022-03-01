import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate('xxxxx-adminsdk-xxxxx-xxxxxxx.json') # from firebase project settings
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://console.firebase.google.com/project/gnetworktest-32569/firestore/data/~2Fdata~2F0BhH3EDJRHdRFfLzSzHS'
})

db = firebase_admin.firestore.client()

# add your collections manually
collection_names = ['myFirstCollection', 'mySecondCollection']
collections = dict()
dict4json = dict()
n_documents = 0

for collection in collection_names:
    collections[collection] = db.collection(collection).get()
    dict4json[collection] = {}
    for document in collections[collection]:
        docdict = document.to_dict()
        dict4json[collection][document.id] = docdict
        n_documents += 1

jsonfromdict = json.dumps(dict4json)

path_filename = "/mypath/databases/firestore.json"
print ("Downloaded %d collections, %d documents and now writing %d json characters to %s" % ( len(collection_names), n_documents, len(jsonfromdict), path_filename ))
with open(path_filename, 'w') as the_file:
    the_file.write(jsonfromdict)