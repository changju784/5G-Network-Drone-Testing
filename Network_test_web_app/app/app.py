from flask import Flask, render_template, flash
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os


app = Flask(__name__)
app.secret_key = "gkfxqywlehgnsgkskeh"

data = os.path.abspath(os.path.dirname(__file__)) + "/src/serviceAccountKey.json"
cred = credentials.Certificate(data)
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/runTest/", methods=['POST'])
def start():
    db.collection('operations').document('operate').set({'test': True})
    flash("Test Running")
    return render_template('home.html')
    # return render_template('home.html', forward_message=forward_message);

@app.route("/stopTest/", methods = ['POST'])
def stop():
    db.collection('operations').document('operate').set({'test':False})
    return render_template('home.html')

@app.route("/MLmodel")
def MLmodel():
    return render_template("ml.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug = True,)
    # app.run()