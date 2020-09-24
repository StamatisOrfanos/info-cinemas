from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient
from lib.cast import safe_cast
import pymongo
import re

# I am using the ChainMap library to convert the positiveResult list to a dicionary
from collections import ChainMap



#This is the blueprint we are going to import to the app.py 
admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

client = MongoClient("mongodb://mongodb:27017/")
db = client["InfoCinemas"]
movies = db["movies"]
users = db["users"]

# This is just the admin home page,where we are going to link all the other pages, 
# but we are going to have the search function 
@admin.route("/")
@admin.route("/adminHome", methods=["GET"])
def adminHome():
    return render_template("adminHome.html", admEmail=session["email"])




#####################################################################################
# This is the method to insert new movies to the database
@admin.route("/insert")
@admin.route("/insertMovie", methods=["GET", "POST"])
def insertMovie():
    if request.method == "GET":
        return render_template("insertMovie.html")
    else:
        # Insert all the data for a movie including title, year, description, screening
        title = request.form["title"]
        year = safe_cast(request.form["year"], int)
        description = request.form["description"]


        # The screening variable is a list with multiple dictionaries so in order
        # to insert the data to the base correctly we are going to take the data from 
        # the form then insert them to a dictionary and finally append them to the 
        # screening list below 
        screening = []
        date = request.form["date"]
        capacity = safe_cast(request.form["capacity"], int)


        # Unfortunately for me, we ALSO need to check if the user inserts a value 
        # bigger than 50 in the capacity variable
        if capacity > 50:
            flash("The value of the capacity needs to be smaller than 50 please")
            return redirect(url_for("admin.insertMovie"))


        dateDict = {"date" : date}
        capacityDict = {"capacity": capacity}

        # We are going to merge the two dictionaries in order to insert them as 
        # one element to the list 
        dateDict.update(capacityDict)
        
        dictionary_copy = dateDict.copy()
        screening.append(dictionary_copy)

        if movies.find_one({"title": title, "year": year}):
            flash(f"The movie with the title {title} and year {year}already exists\nPlease insert one with a different title")
            return redirect(url_for("admin.insertMovie"))
        else:
            canditateMovie = { "title": title, "year": year, "description": description, "screening": screening }
            movies.insert_one(canditateMovie)
            flash(f"The movie with the title '{title}' has been inserted to the database")
            return redirect(url_for("admin.adminHome"))





#####################################################################################
# This is the method to search for movies
@admin.route("/search")
@admin.route("/searchMovie", methods=["GET", "POST"])
def searchMovie():
    if request.method == "GET":
        return render_template("searchMovie.html")
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
            return redirect(url_for("admin.searchMovie"))
        else:
            return render_template("movie.html", movies=result)






#####################################################################################
# With this method we are going to update movies
@admin.route("/update")
@admin.route("/updateMovie", methods=["GET", "POST"])
def updateMovie():
    if request.method == "GET":
        # Initialy we have to print to the user both the title and the year 
        # in order to avoid mistakes of wrong titles or years data.
        titleList = movies.find({})
        return render_template("updateMovie.html", mvList=titleList)
    else:
        # We take the original data that we are going to use in order to 
        # update the movie including the Title, Year and Date, we are not going
        # to use description (too long) or capacity (no reason to do so)
        title = request.form["title"]
        year = safe_cast(request.form["year"], int)
        date = request.form["date"]


        movie = movies.find_one({"title":title, "year":year, "screening.date":date}) 

        # Check if the movie exists in the database even tho I have printed them above  
        if movie is None:
            flash("There is no movie with the data inserted\nPlease try again")
            return redirect(url_for("admin.updateMovie"))



        # After that we are going to ask for all the new attributes updated in the 
        # movie  
        newTitle = request.form["newTitle"]
        newYear = safe_cast(request.form["newYear"], int)
        newDescription = request.form["newDescription"]
        newDate = request.form["newDate"]
        newCapacity = safe_cast(request.form["newCapacity"], int)


        # Check if the user inserts title to update
        if not newTitle:
            finalTitle = title
        else:
            finalTitle = newTitle



        # Check if the user inserts year to update
        if not newYear:
            finalYear = year
        else:
            finalYear = newYear



        # Check if the user inserts description to update
        if not newDescription:
            descriptionDict = movies.find_one({"title":title, "year":year, "screening.date":date})
            finalDescription = descriptionDict["description"]
        else:
            finalDescription = newDescription



        # Check if the user inserts date to update
        if not newDate:
            # By using the dateList we we are going to insert all the dates that are in a dictionary
            # form and in that way we are going to loop throuth them in order to find the 
            # matching date
            dateList = []
            dateList = movies.find_one({"title":title, "year":year, "screening.date":date})   
            for aDate in dateList["screening"]:
                if aDate.get("date") == date:
                    finalDate = aDate.get("date")
                    break
        else:
            finalDate = newDate



        if not newCapacity:
            dateCapList = []
            dateCapList = movies.find_one({"title":title, "year":year, "screening.date":date})
            for aDateCap in dateCapList["screening"]:
                if aDateCap.get("date") == date:
                    finalCapacity = safe_cast(aDateCap.get("screening.capacity"), int)
                    break
        else:
            finalCapacity = newCapacity


        
        # Now we are going to update the movie with all the final variables 
        # whether the user has inserted new data or not we have checked all 
        # the above

        movies.update_one({ "_id": movie["_id"]}, {"$set": {"title": finalTitle, "year": finalYear, "description": finalDescription} })
        movies.update_one({ "_id": movie["_id"]}, {"$pull": {"screening": {"date": date}} })
        movies.update_one({ "_id": movie["_id"]}, {"$push": {"screening": {"date": finalDate, "capacity": finalCapacity}}})
        flash("The movie has been updated")
        return redirect(url_for("admin.adminHome"))

    





###############################################################################
# This is the method to delete movies 
@admin.route("/delete")
@admin.route("/deleteMovie", methods=["GET", "POST"])
def deleteMovie():
    if request.method == "GET":
        
        # We need to take only the values of the title key and not the key, so after 
        # we take the dictionaries {"title": actuallName} we are going to make a list
        # with the actuallNames using the dictionary.get("title") command
        # Knowledge from the link : tutorialspoint.com/python/dictionary_get.htm

        titleList = movies.find({}, {"_id": 0, "year": 0, "description":0, "screening":0})
        return render_template("deleteMovie.html", allMovies=titleList)
    else:
        title = request.form["title"]
        moviesWithTitle = movies.find({"title": title}).count()

        if moviesWithTitle == 0:
            flash(f"There is no movie with this title")
            return redirect(url_for("admin.deleteMovie"))
        elif moviesWithTitle == 1:
            movies.delete_one({"title": title})
            flash(f"You have successfully deleted the movie {title}")
            return redirect(url_for("admin.adminHome"))
        else:
            # In case we have more than one movie with the same title we are going to 
            # sort them in ascending order in order to have the record with the smallest
            # year as the first record and then we remove it.
            OldestMovie = movies.find({"title": title}).sort({"year": pymongo.ASCENDING})[0]
            movies.delete_one(OldestMovie)
            return redirect(url_for("admin.adminHome"))



####################################################################################
# With this method we are going to change the category of user to admin
@admin.route("/user")
@admin.route("/userModification", methods=["GET", "POST"])
def modifyUser():
    if request.method == "GET":
        userEmails = users.find({})
        return render_template("modifyUser.html", users=userEmails)
    else:
        email = request.form["email"]

        # Initially we check if the user exists and if it is aleady an admin
        actualUser = users.find_one({"email": email})
        if actualUser is None:
            flash(f"There is no user in the database with the email address: {email}")
            return redirect(url_for("admin.modifyUser"))
        elif actualUser["category"] == "admin":
            flash(f"The user with the email address {email} is already an admin")
            return redirect(url_for("admin.modifyUser"))
        else:
            users.update({"email": email}, {"$set": {"category": "admin"}}, True)
            flash(f'The user with the email {actualUser["email"]} has been promoted to admin')
            return redirect(url_for("admin.adminHome"))     
