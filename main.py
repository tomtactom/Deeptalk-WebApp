# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 16:24:52 2020
Version: 0.1v
@author: Luca, Tom
"""

from flask import *
from random import randint
from MyLibs import db, configure, logger

app = Flask(__name__)
app.secret_key = configure.Session_Secret_Key

@app.route('/admin', methods=['GET', 'POST'])# Login seite
def admin():
    if request.method == "GET":
        logger.log( ip=request.remote_addr,message="Hat die admin-login Seite aufgerufen")
        if session.get("login"):

            if db.check_login(session["login"]):
                logger.log( ip=request.remote_addr, message="Ist als Admin eingeloggt")
                return render_template("admin.html", loggedin=True, question_count=db.get_question_count(), rooms_count=db.get_rooms_count(), user_count=db.get_user_count(), questions=db.get_questions())
        else:
            logger.log( ip=request.remote_addr, message="Hat eine falsche Admin-Session benutzt")
            return render_template("admin.html")
    elif request.method == "POST":
        if "login" in request.form:
            if "password" in request.form and db.check_password(request.form["password"]):
                # create session with password hash
                logger.log( ip=request.remote_addr, message="Hat sich eingeloggt")
                session["login"] = configure.admin_pw_hash
                db.clear_statistics()
                return render_template("admin.html", loggedin=True, question_count=db.get_question_count(), user_count=db.get_user_count(), rooms_count=db.get_rooms_count(), questions=db.get_questions())
            else:
                logger.log( ip=request.remote_addr, message="Hat ein falsches Passwort benutzt")
                return render_template("admin.html", message="Falsches Passwort. Bitte lade die Seite neu und versuche erneut dich anzumelden")
        elif session and session["login"]:
            if db.check_login(session["login"]):
                if "new_question" in request.form:
                    if "question" in request.form:
                        if len(request.form["question"]) < 10 or len(request.form["question"]) > 255:
                            session.clear()
                            return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")
                        else:
                            logger.log( ip=request.remote_addr, message="Hat die Frage: '" + request.form["question"] + "' hinzugefügt")
                            return render_template("admin.html", loggedin=True, question_count=db.get_question_count(), user_count=db.get_user_count(), rooms_count=db.get_rooms_count(), message=db.add_question(request.form["question"]), questions=db.get_questions())

                    else:
                        session.clear()
                        return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")

                elif "delete" in request.form:
                    if "id" in request.form:
                        try:
                           val = int(request.form["id"])
                        except ValueError:
                            session.clear()
                            return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")
                        logger.log( ip=request.remote_addr, message="Hat hat Frage " + request.form["id"]  + " gelöscht")
                        return render_template("admin.html", loggedin=True, question_count=db.get_question_count(), user_count=db.get_user_count(), rooms_count=db.get_rooms_count(), message = db.delete_question(request.form["id"]), questions=db.get_questions())
                    else:
                        session.clear()
                        return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")

                elif "update" in request.form:
                    if "question" in request.form and "id" in request.form:
                        try:
                           val = int(request.form["id"])
                        except ValueError:
                           session.clear()
                           return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")

                        if len(str(request.form["question"])) < 10 or len(str(request.form["question"])) > 255:
                            session.clear()
                            return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")
                        else:
                            logger.log( ip = request.remote_addr, message="Hat Frage " + request.form["id"] + " geändert")
                            return render_template("admin.html", loggedin=True, question_count=db.get_question_count(), user_count=db.get_user_count(), rooms_count=db.get_rooms_count(), message=db.update_question(request.form["id"], request.form["question"]) , questions=db.get_questions())

                    else:

                        session.clear()
                        return render_template("admin.html", message = "Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")

                else:
                    session.clear()
                    return render_template("admin.html", message="Ungültiger Request. Bitte lade die Seite neu und versuche es erneut.")
            else:
                return render_template("admin.html", message="Du bist nicht angemeldet.")

        else:
            return render_template("admin.html", message="Ungültiger Request. Bitte lade die Seite neu und versuche erneut dich anzumelden")

@app.route('/', methods=['GET', 'POST'])# Login seite
def main():
    if session:
        #session.clear()
        pass
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
                return render_template("rooms.html", members=db.get_members(room_id), question=db.get_actual_question(room_id), user=int(user_id), activeuser=db.get_active_user(room_id), color=configure.matching_color[randint(0,len(configure.matching_color)-1)], room=roomID)
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
                    if request.form["next_player"]: # Neue Frage
                        activeuser_id = db.change_active_user(int(user_id), room_id)
                        return render_template("rooms.html", members=db.get_members(room_id), question=db.get_new_question(room_id), user=int(user_id), activeuser=activeuser_id, color=configure.matching_color[randint(0,len(configure.matching_color)-1)], room=roomID)

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
        if session:
            session.clear()
        return render_template("invite.html", room_id_crypt=roomID )

# Ajax
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
            return("Etwas hat nicht funktioniert(Keine Session da)...")

# Ajax
@app.route('/question', methods=['GET'])
def get_question():
    if request.method == "GET":
        if session.get("session"):
            user_id, room_id = session["session"]
            if db.check_session(user_id, room_id) == True:
                return render_template("question.ajax.html", question=db.get_actual_question(room_id), activeuser=db.get_active_user(room_id), user=int(user_id))
        else:
            return("Etwas hat nicht funktioniert(Session nicht vorhanden)...")

# Ajax
@app.route('/statistics', methods=['GET'])
def get_statistics():
    if request.method == "GET":
        if session and session["login"]:
            if db.check_login(session["login"]):
                db.clear_statistics()
                return render_template("statistics.ajax.html", question_count=db.get_question_count(), user_count=db.get_user_count(), rooms_count=db.get_rooms_count())
            else:
                session.clear()
                return redirect("/")
        else:
            session.clear()
            return redirect("/")


# Ajax
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

# Logout
@app.route('/logout', methods=['POST', "GET"])
def logout():
    if request.method == "POST" or request.method == "GET":
        if session:
            if session.get("session"):
                user_id, room_id = session["session"]
                if db.check_session(user_id, room_id) == True:
                    db.delete_user(user_id, room_id)
            session.clear()
            return redirect("/")
        else:
            return redirect("/")

@app.errorhandler(404)
def internal_error(e):
    return redirect("/")



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

# Einladungslink teilen Button  --> Design
# Admin seite passwörter ändern
# Online configure.py Editor

# Impressum/Datenschutz
# Kontaktformularseite &  Eigene Fragen einreichen
# Ausführliche Dokumentation und Anleitung/Erklärung
# Räume und User als Ordnerstruktur
# Alte Räume automatisch löschen
