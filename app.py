import os
from re import compile
from pymongo import MongoClient
from flask import Flask, Blueprint, render_template, request, redirect, session, url_for, flash

# Local libraries that I made, in order to have a clean app.py and call the methods 
# needed through the packages in the project
from lib.cast import safe_cast
from lib.populate import insert_json
from methods.authentication import authentication
from methods.admin import admin
from methods.user import user



# Connect to mongodb and make the collections variables 
client = MongoClient("mongodb://mongodb:27017/")
db = client["InfoCinemas"]
movies = db["movies"]
users = db["users"]

# Create flask app and add secret key
app = Flask(__name__)
app.secret_key = "INFOCIMENAS_SECRET"


# The following are the blueprints we are going to use to have 
# this app.py clean to use for you guys
app.register_blueprint(authentication, url_prefix="/au")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(user, url_prefix="/user")



@app.route("/home", methods=["GET"])
def index():
    return "<h2>Welcome to the InfoCinemas Website</h2>"
    


# No matter the situation we are going to send the user to the sign-in page
@app.route("/")
@app.route("/login")
@app.route("/signIn")
def routeToLogin():
    return redirect(url_for("authentication.signIn"))
       


if __name__ == "__main__":
    if not "InfoCinemas" in db.list_collection_names():
     	insert_json("movies.json", movies)
     	insert_json("users.json", users)

    app.run(debug=True, host='0.0.0.0', port=5000)