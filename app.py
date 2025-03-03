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

@app.route("/gyms")
def gyms():
    return render_template("gyms.html")

@app.route("/friends")
def friends():
    current_user_id = ObjectId(current_user.id)
    
    search_query = request.args.get('search', '').strip()

    if search_query:        
        users = mongo.db.login.find({
            "_id": {"$ne": current_user_id},
            "username": {"$regex": search_query, "$options": "i"} 
        })
    else:
        users = mongo.db.login.find({"_id": {"$ne": current_user_id}})

    user_list = []
    for user in users:
        user['_id'] = str(user['_id']) 
        user_list.append(user)

    return render_template("friends.html", users=user_list)

@app.route("/food")
def nutrition():   
    current_user_id = ObjectId(current_user.id)
    
    try:
        all_meals = mongo.db.login.find_one({"_id": current_user_id}) 

        meals = [str(meal['name']) for meal in all_meals['meals']]
    except:
        meals=[]
    
    return render_template("nutrition.html", user_meals=meals)

@app.route("/add_meal",methods = ["GET","POST"])
def add_meal():
    if request.method=="POST":
        current_user_id = ObjectId(current_user.id)

        meal_name=request.form["name"]
        meal_calories=request.form["calories"]
        meal_notes=request.form["notes"]
        mongo.db.login.update_one({"_id": current_user_id},{"$push": {"meals": {"name": meal_name, "calories": meal_calories, "notes":meal_notes}}})

        return redirect(url_for("nutrition"))
    
    return render_template("meal.html")

if __name__ == "__main__":
    app.run(debug=True)
