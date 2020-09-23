from flask import Flask, jsonify



class User:

    def signUp(self):
        user = {
            "_id": "",
            "name": "",
            "email": "",
            "password": "",
            "movies_seen": [],
            "category" : ""
        }
        return jsonify(user), 200


def search_user(users, email):
    return users.find_one({"email": email}) 