import json
from flask import Flask, redirect, render_template, flash, jsonify, request, url_for
import os
import sys

from src.database import Database
from src.ml_engines.model_regression import Modeling


app = Flask(__name__)
app.secret_key = "gkfxqywlehgnsgkskeh"


database = Database()
ml = Modeling()

@app.route("/")
def index():
    return render_template("home.html")


@app.route("/runTest/", methods=['POST','GET'])
def start():
    database.db.collection('operations').document('operate').set({'test': True})
    flash("Test Running")

    doc_ref = database.db.collection('operations').document('newest')
    doc_watch = doc_ref.on_snapshot(database.on_snapshot)

    return render_template('home.html', \
        upload = database.upload,
        download = database.download,
        longitude= database.longitude,
        latitude = database.latitude,
        altitude = database.altitude)



@app.route("/stopTest/", methods = ['POST'])
def stop():
    database.db.collection('operations').document('operate').set({'test':False})
    return render_template('home.html')

@app.route('/update_recent', methods = ['POST'])
def update_recent():

    return jsonify('',render_template('recent_data.html', \
        upload = database.upload,
        download = database.download,
        longitude= database.longitude,
        latitude = database.latitude,
        altitude = database.altitude))



@app.route("/mlmodel", methods = ['POST','GET'])
def mlmodel():
    return render_template("ml.html")

@app.route("/mlmodel/build", methods = ['POST'])
def build_and_train():
    accuracy = ml.train()
    print(accuracy)
    return render_template("train_result.html", accuracy = accuracy)

@app.route("/mlmodel/predict", methods = ['POST','GET'])
def predict():
    output = request.get_json()
    result = json.loads(output) 
    # function predict should take input from the user
    alt = result["altitude"]
    lat = result["latitude"]
    lng = result["longitude"]
    try:
        longitude = float(lng)
        latitude = float(lat)
        altitude = float(alt)
    except:
        msg = "please enter all the input fields correctly"
        return render_template("errorMessage.html", message = msg)
    try:
        prediction = ml.predict(longitude,latitude,altitude)
    except:
        msg = "Please train the model at least once before prediction"
        return render_template("errorMessage.html", message=msg)
    return render_template("prediction.html", upload=prediction[0], download=prediction[1])



@app.route("/mlmodel/maphistory", methods = ['POST'])
def map_history():
    return render_template('map_history.html')

    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug = True,)
    # app.run()