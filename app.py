from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import MongoClient, PyMongo
import os
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://AndrewJung03:hNIc9g8S9chCPoUM@project2.5hfm0.mongodb.net/WorkoutApp?retryWrites=true&w=majority&appName=project2"  
app.config["MONGO_DBNAME"] = "WorkoutApp"
app.config["SECRET_KEY"] = "asdasd123"

mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username, user_id):
        self.username = username
        self.id= user_id

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.login.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(username=user["username"], user_id=str(user["_id"]))
    return None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = mongo.db.login.find_one({"username": username})
        if user and user["password"] == password:
            login_user(User(username=username, user_id=str(user["_id"])))
            return redirect(url_for("homepage"))
        else:
            return render_template('login.html', message="Invalid username/password.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]
        
        if password != password2:
            return render_template('register.html', message="Passwords do not match.")
        
        if mongo.db.login.find_one({"username":username}):
            return render_template('register.html', message="Username already exists.")
        
        mongo.db.login.insert_one({"username": username, "password": password})
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/homepage")

@login_required
def homepage():
    return render_template("homepage.html")

if __name__ == "__main__":
    app.run(debug=True)
