import sqlite3 as sql
import hashlib
from random import randint
from cryptography.fernet import Fernet
import hashlib

import install

from MyLibs import configure

database = configure.database
password = configure.password
admin_pw_hash = configure.admin_pw_hash
hash_salt = configure.hash_salt

def encrypt(message, key):
    return (Fernet(key).encrypt(message.encode())).decode()

def decrypt(token, key):
    try:
        return (Fernet(key).decrypt(token.encode())).decode()
    except:
        return "None"

def check_login(pass_hash):
    if pass_hash == admin_pw_hash:
        return True
    else:
        return False

def change_admin_password(admin_password):
    admin_password_hash = hashlib.sha512(bytes(admin_password + configure.hash_salt, "utf8")).hexdigest()
    install.write(configure.host, configure.port, configure.hash_salt, admin_password_hash, configure.password, configure.Session_Secret_Key)


def delete_user(user_id, room_id):
    print("a wird ausgeführt")
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE user_id='" + str(user_id) + "'")
    con.commit()

    cur.execute("SELECT member_id FROM rooms WHERE room_id='" + str(room_id) + "'")
    member_ids = cur.fetchall()[0][0]
    if str(member_ids) == str(user_id):
        print("last user")
        cur.execute("UPDATE rooms SET member_id='-1' WHERE room_id='" + str(room_id) + "'")
        con.commit()
        cur.execute("UPDATE rooms SET activeuser_id='-1' WHERE room_id='" + str(room_id) + "'")
        con.commit()
    else:
        print("not last")
        active_member_ids = []
        for member_id in member_ids.split(','):
            if member_id != str(user_id):
                active_member_ids.append(member_id)

        active_member_str = ""
        for member in active_member_ids:
            active_member_str += str(member) + ","

        active_member_str = active_member_str[:-1]
        print("###############\n",active_member_str, "\n###########")

        cur.execute("UPDATE rooms SET member_id='" + str(active_member_str) + "' WHERE room_id='" + str(room_id) + "'")
        con.commit()
    con.close()


def get_user_count():
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    active_user_count = cur.fetchall()
    print(active_user_count)
    if active_user_count == []:
        active_user_count = 0
    else:
        active_user_count = active_user_count[0][0]
    cur.execute("SELECT seq FROM sqlite_sequence WHERE name='users'")
    all_users_count = cur.fetchall()
    print(all_users_count)
    if all_users_count==[]:
        all_users_count = 0
    else:
        all_users_count = all_users_count[0][0]
    con.close()
    return((active_user_count, all_users_count)) # (all_actual_online_users, all_users_ever)

def get_rooms_count():
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT seq FROM sqlite_sequence WHERE name='rooms'")
    all_rooms = cur.fetchall()
    print(all_rooms)
    print("room")
    if all_rooms==[]:
        all_rooms = 0
    else:
        all_rooms = all_rooms[0][0]
    con.close()
    return(all_rooms) # (all_rooms)

def get_question_count():
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT seq FROM sqlite_sequence WHERE name='questions'")
    all_rooms = cur.fetchall()[0][0]
    con.close()
    return(all_rooms) # (all_questions)

def check_password(password):
    if hashlib.sha512(bytes(password + hash_salt, "utf8")).hexdigest() == admin_pw_hash:
        return True
    else:
        return False

def update_question(id, question):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("UPDATE questions SET question='" + str(question) + "' WHERE question_id='" + str(id) + "'")
    con.commit()
    con.close()
    return("Die Frage wurde erfolgreich geändert.")

def delete_question(id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("DELETE FROM questions WHERE question_id='" + str(id) + "'")
    con.commit()
    con.close()
    return("Die Frage wurde erfolgreich gelöscht.")

def get_questions():
    con = sql.connect(database)
    cur = con.cursor()

    cur.execute("SELECT question, question_id FROM questions")
    questions = cur.fetchall()
    con.close()

    filtered_questions = []

    for i in questions:
        if bytes(i[0][-1], "utf8") == b'\n':
            filtered_questions.append((i[0][:-1], i[1]))
        else:
            filtered_questions.append((i[0], i[1]))

    return (filtered_questions)

def add_question(question):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT question FROM questions WHERE question='" + str(question) + "'")
    check_if_question_exist = cur.fetchall()
    if check_if_question_exist == []:
        cur.execute("INSERT INTO questions(question) values('" + str(question) + "')")
        con.commit()
        con.close()
        return("Die Frage wurde erfolgreich hinzugefügt.")
    else:
        con.close()
        return("Diese Frage existiert bereits.")

def create_new_room():
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("INSERT INTO rooms DEFAULT VALUES")
    con.commit()
    cur.execute("SELECT room_id FROM rooms ORDER BY room_id DESC LIMIT 1")
    room_id = str(cur.fetchall()[0][0])
    con.close()
    return( encrypt(room_id, password) )

def create_new_user(username, room_id_crypt):
    con = sql.connect(database)
    cur = con.cursor()
    room_id =  decrypt(room_id_crypt, password)
    cur.execute("INSERT INTO users(user_name, room_id) values('" + username + "', '" + room_id + "')")
    con.commit()
    cur.execute("SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1")
    user_id = str(cur.fetchall()[0][0])
    cur.execute("SELECT member_id FROM rooms WHERE room_id='" + room_id + "'")
    member_id = cur.fetchall()[0]
    if member_id[0] != "-1":
        member_id = str(member_id[0]) + "," + str(user_id)
    else:
        member_id = user_id
    cur.execute("UPDATE rooms SET member_id='" + member_id + "' WHERE room_id='" + room_id + "'")
    con.commit()
    cur.execute("SELECT activeuser_id FROM rooms WHERE room_id='" + room_id + "'")
    activeuser_id = cur.fetchall()[0][0]
    if activeuser_id == -1 :
         cur.execute("UPDATE rooms SET activeuser_id='" + user_id + "' WHERE room_id='" + room_id + "'")
         con.commit()
    con.close()
    return( user_id , room_id)

def check_session(user_id, room_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT member_id FROM rooms WHERE room_id='" + room_id + "'")
    member_id = cur.fetchall()
    con.close()
    if member_id == []:
        return(False)
    else:
        member_id = member_id[0][0]
        members = member_id.split(",")
        if user_id in members:
            return(True)
        else:
            return(False)

def check_room_exists(room_id_crypt):
    try:
        room_id = decrypt(room_id_crypt, password)
    except:
            return False
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT room_id FROM rooms WHERE room_id='" + room_id + "'")

    test = cur.fetchall()
    con.close()
    if test == []:
        return False
    else:
        test = test[0][0]
        return(test != None)

def get_members(room_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT member_id FROM rooms WHERE room_id='" + room_id + "'")
    member_id = cur.fetchall()[0][0]
    cur.execute("SELECT user_name, user_id FROM users WHERE user_id IN (" + str(member_id) + ")")
    members = cur.fetchall()
    con.close()
    return(members)# [(username, userid)]

def get_user_by_id(user_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT user_name FROM users WHERE user_id='" + str(user_id) + "'")
    user_name = cur.fetchall()
    if user_name == []:
        user_name = (None, None)
    else:
        user_name = user_name[0][0]

    con.close()
    return(user_name)# username

def get_active_user(room_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT activeuser_id FROM rooms WHERE room_id='" + room_id + "'")
    activeuser_id = cur.fetchall()
    if activeuser_id:
        activeuser_id = activeuser_id[0][0]
        return((activeuser_id, get_user_by_id(activeuser_id))) # (userid, username)
    else:
        return((0, False))

def check_active_player(user_id, room_id):
    return int(get_active_user(room_id)[0]) == int(user_id)

def change_active_user(user_id, room_id):
    members = get_members(room_id)
    activeuser_id = int(user_id)
    for i in range(len(members)):

        if members[i][1] == activeuser_id:

            if len(members) == 1:
                break
            elif len(members) == i + 1:
                activeuser_id = members[0][1]
                break
            else:

                activeuser_id = members[i+1][1]
                break

    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("UPDATE rooms SET activeuser_id='" + str(activeuser_id) + "' WHERE room_id='" + room_id + "'")
    con.commit()
    con.close()
    return((activeuser_id, get_user_by_id(activeuser_id)))


def get_actual_question(room_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT actual_question FROM rooms WHERE room_id='" + str(room_id) + "'")
    question_id = cur.fetchall()[0][0]
    cur.execute("SELECT question FROM questions WHERE question_id='" + str(question_id) + "'")
    question = cur.fetchall()[0][0]
    con.close()
    return(question)

def get_new_question(room_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT passed_questions FROM rooms WHERE room_id='" + str(room_id) + "'")
    passed_questions = cur.fetchall()[0][0]
    cur.execute("SELECT question_id, question FROM questions WHERE question_id NOT IN (" + str(passed_questions) + ")")
    possible_questions = cur.fetchall()
    if not len(possible_questions) == 0:
        question_pos = randint(0, len(possible_questions) - 1)
        question = possible_questions[question_pos]
        cur.execute("UPDATE rooms SET passed_questions='" + str(passed_questions) + "," + str(question[0]) + "' WHERE room_id='" + room_id + "'")
        con.commit()
        cur.execute("UPDATE rooms SET actual_question='" + str(question[0]) + "' WHERE room_id='" + str(room_id) + "'")
        con.commit()
        question = question[1]
    else:
        cur.execute("UPDATE rooms SET passed_questions='1' WHERE room_id='" + str(room_id) + "'")
        con.commit()
        cur.execute("UPDATE rooms SET actual_question='1' WHERE room_id='" + str(room_id) + "'")
        con.commit()
        question = get_actual_question(room_id)

    con.close()
    return(str(question))

def update_active(user_id, room_id, only_update=False):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("UPDATE users SET timestamp = CURRENT_TIMESTAMP WHERE user_id = " + str(user_id))#
    con.commit()
    con.close()
    if only_update == False:
        remove_timeouted_user(user_id, room_id)
    return("True")

def check_user_exists(user_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id='" + str(user_id) + "'")
    user_id = cur.fetchall()
    if user_id == [] or user_id == False or user_id == [()]:
        return(False)
    else:
        return(True)

def clear_statistics():
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE timestamp <= strftime('%Y-%m-%d %H:%M:%S','now','-22 seconds')")
    con.commit()
    con.close()



def remove_timeouted_user(user_id, room_id):
    con = sql.connect(database)
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE timestamp <= strftime('%Y-%m-%d %H:%M:%S','now','-22 seconds')")
    con.commit()

    cur.execute("SELECT member_id FROM rooms WHERE room_id='" + str(room_id) + "'")
    member_ids = cur.fetchall()[0][0]
    active_member_ids = []
    for member_id in member_ids.split(','):
        if check_user_exists(member_id):
            active_member_ids.append(member_id)

    active_member_str = ""
    for member in active_member_ids:
        active_member_str += str(member) + ","

    active_member_str = active_member_str[:-1]

    cur.execute("UPDATE rooms SET member_id='" + str(active_member_str) + "' WHERE room_id='" + str(room_id) + "'")

    con.commit()


    active_user = get_active_user(room_id)[0]
    if not check_user_exists(active_user):
        print("change active")
        cur.execute("UPDATE rooms SET activeuser_id ='" + str(user_id) + "' WHERE room_id='" + str(room_id) + "'")
        con.commit()

    con.close()

    # delete empty room
