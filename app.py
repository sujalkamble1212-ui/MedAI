import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


#secretkey

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"


# MONGODB string 

app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)
try:
    mongo.cx.server_info()
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection failed:", e)



users_collection = mongo.db.users
history_collection = mongo.db.history


#  LOGIN MANAGER 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "error"


#  USER  

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):

    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if user:
        return User(str(user["_id"]), user["username"])

    return None


#  ML MODEL 

model = joblib.load("disease_model.pkl")


#  ROUTES 


# ---------- HOME ----------

@app.route("/")
def home():
    slides = [
        {"image": "images/l1.png" ,"mobile_image": "images/l1mobile.png"},
        {"image": "images/l2.png" ,"mobile_image": "images/l2mobile.png"},
        {"image": "images/l3.png" ,"mobile_image": "images/l3mobile.png"}
    ]
    return render_template("index.html", user=current_user ,slides=slides)


# ---------- REGISTER ----------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        existing_user = users_collection.find_one({"username": username})

        if existing_user:
            flash("Username already exists!","error")
            return redirect(url_for("register"))

        users_collection.insert_one({
            "username": username,
            "password": password
        })

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


#  LOGIN 

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):

            user_obj = User(str(user["_id"]), user["username"])
            login_user(user_obj)

            return redirect(url_for("home"))

        else:
            flash("Invalid username or password!","error")

    return render_template("login.html")


#  ANALYZE  

@app.route("/analyze")
@login_required
def dashboard():

    df = pd.read_csv("dataset.csv")
    symptoms = list(df.columns[:-1])

    return render_template(
        "analyze.html",
        symptoms=symptoms,
        user=current_user
    )


#  PREDICT 

@app.route("/predict", methods=["POST"])
@login_required
def predict():

    try:

        data = request.json

        selected_symptoms = [k for k, v in data.items() if v == 1]

        input_data = np.array([list(data.values())])

        prediction = model.predict(input_data)[0]
        probability = int(max(model.predict_proba(input_data)[0]) * 100)

        history_collection.insert_one({
            "user_id": current_user.id,
            "disease": prediction,
            "probability": probability,
            "symptom_count": len(selected_symptoms),
            "symptoms": ", ".join(selected_symptoms),
            "date": datetime.utcnow()
        })

        return jsonify({
            "predicted_disease": prediction,
            "probability": probability
        })

    except Exception as e:

        print("Prediction Error:", e)

        return jsonify({
            "predicted_disease": "Error",
            "probability": 0
        }), 500


#  HISTORY 

@app.route("/history")
@login_required
def history():

    records = history_collection.find({
        "user_id": current_user.id
    }).sort("date", -1)

    history_data = []

    for r in records:

        history_data.append({
            "date": r["date"].strftime("%Y-%m-%d"),
            "disease": r["disease"],
            "probability": r["probability"],
            "symptom_count": r["symptom_count"],
            "symptoms": r["symptoms"]
        })

    return render_template("history.html", history=history_data)


# LOGOUT 

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)
