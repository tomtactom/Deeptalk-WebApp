# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 16:24:52 2020
Version: 0.1v
@author: Luca, Tom
"""

from flask import *
from random import randint
from MyLibs import db, configure

app = Flask(__name__)
app.secret_key = configure.Session_Secret_Key


@app.route('/', methods=['GET', 'POST'])# Login seite
def main():
    if request.method == "POST":
        if request.form["create_room"]:
            room_id = db.create_new_room()
            return(redirect("/invite/"+room_id))
    elif request.method == "GET":
        #
        return render_template("index.html")
        

@app.route('/rooms/<roomID>', methods=['GET', 'POST'])# Haupt Seite
def rooms(roomID):
    if request.method == "GET":
        if session.get("session"):
            user_id, room_id = session["session"]
            if db.check_session(user_id, room_id) == True:
                db.update_active(user_id, room_id, only_update=True)
                return render_template("rooms.html", members=db.get_members(room_id), question=db.get_actual_question(room_id), user=int(user_id), activeuser=db.get_active_user(room_id), color=configure.matching_color[randint(0,len(configure.matching_color)-1)])
            else:
                session.clear() # Session löschen, wenn der Nutzer nicht in der Datenbank gefunden wurde.
                return(redirect("/invite/" + db.encrypt(room_id, db.password)))
        else:
            return(redirect("/invite/" + roomID))

    if request.method == "POST":
        if session.get("session"):
            user_id, room_id = session["session"]
            if db.check_session(user_id, room_id) == True and room_id == db.decrypt(roomID, db.password):
                db.update_active(user_id, room_id, only_update=True)
                if db.check_active_player(user_id, room_id):
                    if request.form["next_player"]:
                        activeuser_id = db.change_active_user(int(user_id), room_id)
                        return render_template("rooms.html", members=db.get_members(room_id), question=db.get_new_question(room_id), user=int(user_id), activeuser=activeuser_id, color=configure.matching_color[randint(0,len(configure.matching_color)-1)])
                
@app.route('/invite/<roomID>', methods=['POST', 'GET'])# Invite Seite
def invite(roomID):
    if request.method == "POST":
        if request.form["username"] and request.form["room_id_crypt"]:
            if db.check_room_exists(request.form["room_id_crypt"]):
                username = request.form["username"]
                room_id_crypt = request.form["room_id_crypt"]
                user_id, room_id = db.create_new_user(username, room_id_crypt )
                session["session"] = (user_id, room_id)
                return(redirect("/rooms/" + room_id_crypt ))
            return(render_template("invite.html", message="Dieser Raum existiert nicht..."))
        return(render_template("invite.html", message="Etwas hat nicht funktioniert..."))
    elif request.method == "GET":
        return render_template("invite.html", room_id_crypt=roomID )

@app.route('/members', methods=['GET'])
def get_members():
    if request.method == "GET":
        if session.get("session"):
            user_id, room_id = session["session"]
            if db.check_session(user_id, room_id) == True:
                return render_template("members.ajax.html", members=db.get_members(room_id), activeuser=db.get_active_user(room_id), user=int(user_id))
            else:
                return("keine session vorhanden")
        else:
            return("Etwas hat nicht funktioniert...")
        
@app.route('/question', methods=['GET'])
def get_question():
    if request.method == "GET":
        if session.get("session"):
            user_id, room_id = session["session"]
            if db.check_session(user_id, room_id) == True:
                return render_template("question.ajax.html", question=db.get_actual_question(room_id), activeuser=db.get_active_user(room_id), user=int(user_id))
        else:
            return("Etwas hat nicht funktioniert...")

@app.route('/check-active', methods=['GET'])
def check_active():
    if request.method == "GET":
        if session.get("session"):
            user_id, room_id = session["session"]
            if db.check_session(user_id, room_id) == True:
                return db.update_active(user_id, room_id)
            return("keine session vorhanden")
        else:
            return("Etwas hat nicht funktioniert...")

@app.errorhandler(500)
def internal_error(e):
	return render_template("error/500.html")

if __name__ == "__main__":
	app.run(
		debug =       configure.debug, # Wird nicht gedebugt
		host =        configure.host,# Host setzen
		threaded =    configure.threaded,# Multithreading erlaubt mehrere Clients gleichzeitig
		port =        configure.port # Port setzen
		)


# User aktivität überprüfen
# Fragen mit rooms tabbel abgleichen
