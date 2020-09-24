from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient

#This is the blueprint we are going to import to the app.py 
authentication = Blueprint("authentication", __name__, static_folder="static", template_folder="templates")

client = MongoClient("mongodb://mongodb:27017/")
db = client["InfoCinemas"]
movies = db["movies"]
users = db["users"]


# The following is the sign-up method to make new users, in order to use them
# through the database
@authentication.route("/signUp", methods=["GET", "POST"])
def signUp():
    if "email" in session:
        flash("You are alredy signed in with the following user data:")
        return redirect(url_for("authentication.userInformation"))

    if request.method == "GET":
         # We provide the page to the user
        return render_template("signUp.html")
    else:
        # We insert the name,email of the user and the password as well
        userName = request.form["name"]
        userEmail = request.form["email"]
        userPassword = request.form["password"]

        # Check if the user already exists in the database, since we are going to use the email as the 
        # key of the mogno documents
        userExists = users.find({"email": userEmail}).count()
        if userExists == 0:
            user = {"name": userName, "email": userEmail, "password": userPassword, "movies_seen": [], "category": "user" }
            users.insert_one(user)

            #At this point we start a session so we have to use the session variable 
            session["email"] = userEmail
            return redirect(url_for("authentication.userInformation"))
        else:
            flash(f"A user with this email already exists")
            return redirect(url_for("authentication.signUp"))


# The following is the sign-in method to get to the website and check before 
# every action
@authentication.route("/")
@authentication.route("/signIn", methods=["GET", "POST"])
def signIn():
    # Check if there is a user signed-in already and we redirect them to the user info page
    if "email" in session:
        return redirect(url_for("authentication.userInformation"))

    # We provide the login page to the user
    if request.method == "GET":
        return render_template("signIn.html")
    else:

        userEmail = request.form["email"]
        userPassword = request.form["password"]

        # Check if the user exists in database
        userExists = users.find_one({"email": userEmail})

        # Check if user exists
        if userExists is None:
            flash("There is no user with this email")
            return redirect(url_for("authentication.signIn"))
        else:
            # Check if the password is right 
            if userPassword == userExists["password"]:
                session["email"] = userEmail
            
                if userExists["category"] == "admin":
                    # We check if the user is an admin in order to redirect them to 
                    # the right home page
                    return redirect(url_for("admin.adminHome"))
                else:
                    return redirect(url_for("user.userHome"))
            else:
                # If the user password is wrong redirect to the logIn
                return redirect(url_for("authentication.signIn"))


# The following is the userInformation method check the name,email and category
# of a certain user through the database
@authentication.route("/userInformation", methods=["GET"])
def userInformation():

    if "email" in session:
        # We are going to find the user by the email and parse the 
        # general information of it to print it on the user information 
        # page 
        theUser = users.find_one({"email": session["email"]})

        return render_template("userInformation.html", usrName=theUser["name"], usrEmail=theUser["email"], usrCategory=theUser["category"] )
    else:
        flash("You are not signed in to this website")
        # If we do not have a user in session and tries to go to the userInformation page
        # we are going to redirect them to the sign in
        return redirect(url_for("authentication.signIn"))
        


@authentication.route("/signOut", methods=["GET", "POST"])
def signOut():
    if request.method == "GET":
        # We need to show to the user the kind of account he/she is using
        theUser = users.find_one({"email": session["email"]})

        return render_template("signOut.html", usrName=theUser["name"], usrEmail=theUser["email"])
    else:
        session.pop("email", None)
        flash("You have successfully signed out of the website", "info")
        return redirect(url_for("authentication.signIn"))
    
