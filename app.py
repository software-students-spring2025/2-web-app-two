from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import MongoClient, PyMongo
import os
from bson import ObjectId
import dotenv 

dotenv.load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["MONGO_DBNAME"] = os.getenv("DB_NAME")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

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

@login_required
@app.route("/gyms")
def gyms():
    return render_template("gyms.html")

@login_required
@app.route("/workouts")
def workouts():   
    current_user_id = ObjectId(current_user.id)
    
    try:
        all_user_data = mongo.db.login.find_one({"_id": current_user_id})

        workouts = all_user_data.get('workouts', [])
        workouts.reverse()  
    except:
        workouts = []
    return render_template("workouts.html", workouts=workouts)

@login_required
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

@login_required
@app.route("/food")
def nutrition():   
    current_user_id = ObjectId(current_user.id)
    
    try:
        all_user_data = mongo.db.login.find_one({"_id": current_user_id})

        username = all_user_data.get('username', 'Unknown User') 
        workouts = all_user_data.get('workouts', [])
        meals = all_user_data.get('meals', [])
    except:
        username = 'Unknown User'
        workouts = []
        meals = []
    
    meals.reverse()

    return render_template("/nutrition.html", username=username, workouts=workouts, meals=meals)

@login_required
@app.route("/add_meal", methods=["GET", "POST"])
def add_meal():
    if request.method == "POST":
        current_user_id = ObjectId(current_user.id)
        meal_name = request.form["name"]
        meal_calories = request.form["calories"]
        meal_date = request.form["date"]
        meal_notes = request.form["notes"]

        mongo.db.login.update_one(
            {"_id": current_user_id}, 
            {"$push": {
                "meals": {
                    "meal_id": ObjectId(),
                    "name": meal_name,
                    "calories": meal_calories,
                    "date": meal_date,
                    "notes": meal_notes
                }
            }}
        )

        return redirect(url_for("nutrition"))  
    return render_template("meal.html") 


@login_required
@app.route("/add_workouts", methods=["GET", "POST"])
def add_workouts():
    if request.method == "POST":

        current_user_id = ObjectId(current_user.id)
        workout_name = request.form["name"]
        workout_calories = request.form["calories"]
        workout_dates = request.form["date"]
        workout_notes = request.form["notes"]
        workout_sets = request.form["sets"]
        workout_reps = request.form["reps"]

        mongo.db.login.update_one(
            {"_id": current_user_id},
            {
                "$push": {
                    "workouts": {
                        "_id": ObjectId(),
                        "name": workout_name,
                        "calories": workout_calories,
                        "reps": workout_reps,
                        "sets": workout_sets,
                        "date": workout_dates,
                        "notes": workout_notes
                    }
                }
            }
        )
        return redirect(url_for("workouts"))
    
    return render_template("add_workouts.html")

@login_required
@app.route("/edit_workout/<workout_id>", methods=["GET", "POST"])
def edit_workout(workout_id):
    current_user_id = ObjectId(current_user.id)

    workout = mongo.db.login.find_one(
        {"_id": current_user_id, "workouts._id": ObjectId(workout_id)},
        {"workouts.$": 1} 
    )

    workout = workout["workouts"][0]

    if request.method == "POST":
        updated_name = request.form["name"]
        updated_calories = request.form["calories"]
        updated_reps = request.form["reps"]
        updated_sets = request.form["sets"]
        updated_date = request.form["date"]
        updated_notes = request.form["notes"]

        mongo.db.login.update_one(
            {"_id": current_user_id, "workouts._id": ObjectId(workout_id)},
            {
                "$set": {
                    "workouts.$.name": updated_name,
                    "workouts.$.calories": updated_calories,
                    "workouts.$.reps": updated_reps,
                    "workouts.$.sets": updated_sets,
                    "workouts.$.date": updated_date,
                    "workouts.$.notes": updated_notes,
                }
            }
        )

        return redirect(url_for("workouts"))

    return render_template("edit_workout.html", workout=workout)

@login_required
@app.route("/delete_workout/<workout_id>", methods=["POST"])
def delete_workout(workout_id):
    current_user_id = ObjectId(str(current_user.id)) 
    mongo.db.login.update_one(
        {"_id": current_user_id},
        {"$pull": {"workouts": {"_id": ObjectId(workout_id)}}}
    )

    return redirect(url_for("workouts"))


@login_required
@app.route("/my_profile")
def my_profile():   
    current_user_id = ObjectId(current_user.id)
    
    try:
        all_user_data = mongo.db.login.find_one({"_id": current_user_id})

        username = all_user_data.get('username', 'Unknown User') 
        workouts = all_user_data.get('workouts', [])
        meals = all_user_data.get('meals', [])
    except:
        username = 'Unknown User'
        workouts = []
        meals = []

    return render_template("my_profile.html", username=username, workouts=workouts, meals=meals)

@login_required
@app.route("/edit_meal/<meal_id>", methods=["GET", "POST"])
def edit_meal(meal_id):
    current_user_id = ObjectId(current_user.id)

    meal = mongo.db.login.find_one(
        {"_id": current_user_id, "meals.meal_id": ObjectId(meal_id)},
        {"meals.$": 1} 
    )

    if not meal:
        return redirect(url_for("nutrition")) 

    meal = meal["meals"][0]  

    if request.method == "POST":
        updated_name = request.form["name"]
        updated_calories = request.form["calories"]
        updated_date = request.form["date"]
        updated_notes = request.form["notes"]

        mongo.db.login.update_one(
            {"_id": current_user_id, "meals.meal_id": ObjectId(meal_id)}, 
            {
                "$set": {
                    "meals.$.name": updated_name,
                    "meals.$.calories": updated_calories,
                    "meals.$.date": updated_date,
                    "meals.$.notes": updated_notes,
                }
            }
        )

        return redirect(url_for("nutrition"))  

    return render_template("edit_meal.html", meal=meal, meal_id=meal_id)  

@login_required
@app.route("/delete_meal/<meal_id>", methods=["POST"])
def delete_meal(meal_id):
    current_user_id = ObjectId(str(current_user.id)) 
    mongo.db.login.update_one(
        {"_id": current_user_id},
        {"$pull": {"meals": {"meal_id": ObjectId(meal_id)}}} 
    )

    return redirect(url_for("nutrition")) 


from flask import request

@login_required
@app.route("/user_profile")
def user_profile():   
    user_id = request.args.get('user_id') 

    user_id = ObjectId(user_id)

    user_data = mongo.db.login.find_one({"_id": user_id})  
            
    username = user_data.get('username', 'Unknown User')
    workouts = user_data.get('workouts', [])
    meals = user_data.get('meals', [])

    return render_template("user_profile.html", username=username, workouts=workouts, meals=meals)


@app.route("/404")
def g404():
    return render_template("404.html")

@app.route("/Palladium")
def palladium():
    return render_template("palladium.html")

@app.route("/brooklyn")
def brooklyn_athletic_facility():
    return render_template("brooklyn.html")

@app.route("/paulson")
def paulson_center():
    return render_template("paulson.html")



if __name__ == "__main__":
    app.run(debug=True)
