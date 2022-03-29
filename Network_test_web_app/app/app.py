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

# @app.route("/running/", methods=['POST','GET'])
# def running():
#     database.db.collection('operations').document('operate').set({'test': True})
#     flash("Test Running")

#     doc_ref = database.db.collection('operations').document('newest')
#     doc_watch = doc_ref.on_snapshot(database.on_snapshot)

#     return render_template('running.html')

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
    # return jsonify('',render_template('running.html', \
    #     upload = database.upload,
    #     download = database.download,
    #     longitude= database.longitude,
    #     latitude = database.latitude,
    #     altitude = database.altitude))


@app.route("/mlmodel")
def mlmodel():
    return render_template("ml.html")

@app.route("/mlmodel/build", methods = ['POST'])
def build_and_train():
    accuracy = ml.train()
    flash("The model accuracy is " + str(accuracy))
    return render_template("ml.html")

@app.route("/mlmodel/predict", methods = ['POST'])
def predict():
    #function predict should take input from the user
    try:
        longitude = float(request.form["longitude"])
        latitude = float(request.form["latitude"])
        altitude = float(request.form["altitude"])
    except:
        flash("please enter all the input fields correctly")
        return render_template("ml.html")

    try:
        prediction = ml.predict(longitude,latitude,altitude)
    except:
        flash("Please train the model at least once before prediction")
        return render_template("ml.html")

    flash("The predictions is : " + "  ".join(prediction) )
    return render_template("ml.html")
    # return render_template("googleMap.html")

@app.route("/mlmodel/map", methods = ['POST','GET'])
def googleMap():
    if request.method == 'POST':
        return render_template("googleMap.html")
    elif request.method == 'GET':
        return redirect(url_for('ml'))

    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug = True,)
    # app.run()
