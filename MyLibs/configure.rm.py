import os

matching_color = [
    ("#e67e22","#2c3e50"),
    ("#2980b9","#2c3e50"),
    ("#1abc9c","#2c3e50"),
    ("#3498db","#2c3e50"),
    ("#9b59b6","#2c3e50"),
    ("#f1c40f","#2c3e50"),
    ("#e74c3c","#2c3e50"),
    ("#c0392b","#2c3e50"),
    ("#d35400","#2c3e50"),
    ("#8e44ad","#2c3e50"),
    ("#27ae60","#2c3e50"),
    ("#16a085","#2c3e50"),
    ("#e67e22","#34495e"),
    ("#2980b9","#34495e"),
    ("#1abc9c","#34495e"),
    ("#3498db","#34495e"),
    ("#9b59b6","#34495e"),
    ("#f1c40f","#34495e"),
    ("#e74c3c","#34495e"),
    ("#c0392b","#34495e"),
    ("#d35400","#34495e"),
    ("#8e44ad","#34495e"),
    ("#27ae60","#34495e"),
    ("#16a085","#34495e"),
    ]



if os.name=="nt":
    database = __file__.replace("MyLibs\\configure.py", "") + "Databases\\database.db"
    logfile = __file__.replace("MyLibs\\configure.py", "") + "Databases\\log.csv"
else:
    database = __file__.replace("MyLibs/configure.py", "") + "Databases/database.db"
    logfile = __file__.replace("MyLibs/configure.py", "") + "Databases/log.csv"
debug = False       # Wird nicht gedebugt
host = '0.0.0.0'    # Host setzen
threaded = True     # Multithreading erlaubt mehrere Clients gleichzeitig
port = ''       # Port setzen

hash_salt = "<a random utf8 salt>"  #  Your random hash salt
admin_pw_hash = "<your hashed password>"
# admin_pw_hash  = hashlib.sha512(bytes(<your_password> + hash_salt, "utf8")).hexdigest()
password = "" # password for room_id
Session_Secret_Key = b''
