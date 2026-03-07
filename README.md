# 🩺 MedAI - Disease Prediction Web Application

MedAI is a Flask-based web application that predicts possible diseases based on user symptoms using a trained machine learning model. The application also allows user authentication and stores prediction history using MongoDB.

---

## 🚀 Features

* User Registration and Login
* Disease Prediction using Machine Learning
* Prediction History Storage
* MongoDB Database Integration
* Flask Backend
* Deployable on Render

---

## 🛠 Tech Stack

* Python
* Flask
* MongoDB Atlas
* Scikit-learn
* HTML / CSS
* Render (Deployment)

---

## 📂 Project Structure

```
MedAI/
│
├── app.py
├── disease_model.pkl
├── dataset.csv
├── requirements.txt
├── Procfile
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── result.html
│
├── static/
│   ├── css/
│   └── js/
```

---


## 🗄 Database

The project uses **MongoDB Atlas** for storing:

* User Accounts
* Prediction History

Collections used:

```
user
history
```

---

## 📸 Application Workflow

1. User registers or logs in
2. User enters symptoms
3. Machine learning model predicts disease
4. Result is displayed
5. Prediction history is saved to database

---

## 📌 Future Improvements

* Add more diseases to the model
* Improve UI/UX
* Add doctor recommendations
* Deploy with Docker
* Add API support

---



