from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient
from lib.cast import safe_cast
import pymongo, re

#This is the blueprint we are going to import to the app.py 
user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

client = MongoClient("mongodb://mongodb:27017/")
db = client["InfoCinemas"]
movies = db["movies"]
users = db["users"]



@user.route("/")
@user.route("/userHome", methods=["GET"])
def userHome():
        return render_template("userHome.html", usrEmail=session["email"])




##################################################################
# With this method the user is going to be able to buy tickets to the movie 
# and then add the movie to the movies_seen variable
@user.route("/buy")
@user.route("/buyTickets", methods=["GET", "POST"])
def buyTickets():
    if request.method == "GET":
        movieTitles = movies.find({}, {"_id":0, "description":0})
        return render_template("userBuyTickets.html", mvList=movieTitles)
    else:
        title = request.form["title"]
        year = safe_cast(request.form["year"], int)
        date = request.form["date"]
        numOfTickets = safe_cast(request.form["numTickets"], int)
        movie = movies.find_one({"title": title, "year":year, "screening.date": date})
        
        # Initially we check if the movie exists 
        if movies.find_one({"title": title, "year":year}) is None:
            flash(f"The movie with the title {title} does not exists in the databse")
            return render_template("userBuyTickets.html")

        # Next we have to check if the movie exists with that certain date of screening
        if movie is None:
            flash(f"There is no movie with that screening time")
            return render_template("userBuyTickets.html")

        # We also check the number of tickets the user inserts and we redirect if the 
        # data inserted are not correct
        if numOfTickets < 0 or numOfTickets > 50:
            flash("The number of tickets must be bigger than zero and smaller than 50 or the remainder of the movies's capacity")
            return render_template("userBuyTicket.html")


        # We make the checkList that has all the screening dates and capacity of each date
        # that we are going to use in order to find the capacity of the screening the 
        # user inserts
        checkList = []
        checkList = movies.find_one({"title":title, "year":year, "screening.date": date})
        
        for capDict in checkList["screening"]:
            if capDict.get("date") == date:
                actuallCapacity = safe_cast(capDict.get("capacity"), int)
                break
        
        capacityAfter = actuallCapacity - numOfTickets
        

        # Furthemore we have have to check  
        if  capacityAfter < 0:
            flash("Also the number of tickets you can buy has to be smaller than the capacity of the screening")
            return render_template("userBuyTicket.html")

        # At this point I pull the date and the capacity that match the date that the user 
        # has inserted and then push to that screening the same date but the updated capacity
        # because if I was to just set the new data I would also delete all the other screenings 

        movies.update_one({"_id": movie["_id"]}, {"$pull": {"screening": {"date": date}}})
        movies.update_one({"_id": movie["_id"]}, {"$push": {"screening": {"date": date, "capacity": capacityAfter}}})

        # We also have to update the movies_seen of the user 
        movieDict = movies.find_one({"_id": movie["_id"]})
        lastTitleDict = movieDict["title"]
        users.update_one({"email": session["email"]}, {"$push": {"movies_seen": lastTitleDict}})


        # Need to add to this user the movie 
        flash(f"You have successfully bought tickets to the movie {title}")
        return redirect(url_for("user.userHome"))





##################################################################
@user.route("/history")
@user.route("/movieHistory", methods=["GET"])
def history():
    print(f'The current user is {session["email"]}')
    currentUser = users.find({"email": session["email"]})
    return render_template("history.html", data=currentUser)



        
##################################################################
# This is the method to search for movies
@user.route("/search")
@user.route("/searchMovie", methods=["GET", "POST"])
def searchMovie():
    if request.method == "GET":
        return render_template("userSearchMovie.html")
    else:
        # We initially take the title and the year from the user 
        title = request.form["title"]
        year = safe_cast(request.form["year"], int)

        # We use the pattern variable to achieve the search result according to 
        # the exercise. So we do not have to type in the title with the last
        # detail
        pattern = re.compile(f"{title}*")

        # We initialise the result variable where we are going to store the 
        # movies found in the database that have a certain pattern.
        result = None

        # If we do not enter a year then we are going to search based on the pattern
        # of the title
        if year == 0:
            result = movies.find({"title": pattern})
        else:
            # If we insert the year variable we are going to search based
            # on both the title and the year again using the pattern tho.
            result = movies.find({ "$and": [ {"title": pattern}, { "year":year} ]})

        if result.count() == 0:
            flash(f"There is no movie with the title {title}")
            return redirect(url_for("user.searchMovie"))
        else:
            return render_template("userMovie.html", movies=result)