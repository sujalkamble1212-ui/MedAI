import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

# ================= DATABASE CONFIG =================


database_url = os.environ.get("DATABASE_URL")

if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ================= LOAD ML MODEL =================

model = joblib.load("disease_model.pkl")

# ================= DATABASE MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease = db.Column(db.String(100))
    probability = db.Column(db.Integer)
    symptom_count = db.Column(db.Integer)
    symptoms = db.Column(db.Text)   # ✅ ADD THIS
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

with app.app_context():
    db.create_all()
    print("Database created successfully!")
        
     
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= ROUTES =================

# ---------- LANDING ----------
@app.route("/")
def home():
    return render_template("index.html", user=current_user)

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!")

    return render_template("login.html")

# ---------- ANALYZE + PREDICT (SAME PAGE) ----------
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

# ---------- PREDICT (AJAX) ----------
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        data = request.json

        # Convert symptoms dictionary to list
        selected_symptoms = [key for key, value in data.items() if value == 1]

        # Convert to model input (example binary list)
        input_data = np.array([list(data.values())])

        # ML prediction
        prediction = model.predict(input_data)[0]
        probability = int(max(model.predict_proba(input_data)[0]) * 100)

        # Save to database
        new_record = History(
            disease=prediction,
            probability=probability,
            symptom_count=len(selected_symptoms),
            symptoms=", ".join(selected_symptoms),  # ✅ store symptoms
            user_id=current_user.id
        )

        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            "predicted_disease": prediction,
            "probability": probability
        })

    except Exception as e:
        print("❌ Prediction Error:", e)

        # Save to DB
        new_record = History(
            user_id=current_user.id,
            symptoms=str(data),
            prediction=prediction,
            probability=probability
        )

        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            "predicted_disease": prediction,
            "probability": probability
        })
        
        

    except Exception as e:
        print("❌ Prediction Error:", e)
        return jsonify({
            "predicted_disease": "Error",
            "probability": 0
        }), 500

# ---------------- HISTORY ----------------
@app.route("/history")
@login_required
def history():

    records = History.query.filter_by(
        user_id=current_user.id
    ).order_by(History.id.desc()).all()

    history_data = []

    # If database has records
    if records:
        for record in records:
            history_data.append({
                "date": record.date.strftime("%Y-%m-%d"),
                "disease": record.disease,
                "probability": record.probability,
                "symptom_count": record.symptom_count
            })

    # If empty → sample data
    else:
        history_data = [
            {
                "date": "2026-03-03",
                "disease": "Flu",
                "probability": 82,
                "symptom_count": 5
            }
            
        ]

    return render_template("history.html", history=history_data)

# ---------- LOGOUT ----------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


   
# ================= RUN =================

if __name__ == "__main__":
   

    app.run(debug=True)




