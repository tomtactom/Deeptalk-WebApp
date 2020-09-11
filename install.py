import random
import string
import hashlib
import os
from cryptography.fernet import Fernet

def full_install():
    if not os.path.exists("./MyLibs/configure.py"):

        def get_random_alphaNumeric_string(stringLength=8):
            lettersAndDigits = string.ascii_letters + string.digits
            return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

        host = input("The ip or domain your web-app is listening to (default=0.0.0.0): ") or "0.0.0.0"
        port = "80"
        while type(port) != int:
            try:
                port = input("The port your web-app is listening to (default=80). Make sure the port is unused and open1: ") or "80"
                port = int(port)
                while int(port) < 1 or int(port) > 65535:
                    port = input("The port your web-app is listening to (default=80). Make sure the port is unused and open2: ") or "80"
                    port = int(port)
                break
            except:
                print("The port mus be an integer between 0 and 65535")


        admin_password = ""
        while not admin_password:
            print("Please enter a valid password")
            admin_password = input("The password you use to login to the controll center: ")

        hash_salt = get_random_alphaNumeric_string(32)
        admin_password_hash = hashlib.sha512(bytes(admin_password + hash_salt, "utf8")).hexdigest()

        password = Fernet.generate_key()
        Session_Secret_Key = get_random_alphaNumeric_string(64)

        write(host, port, hash_salt, admin_password, password, Session_Secret_Key)

        if os.path.exists("./Databases/database.rm.db"):
            os.rename(r'./Databases/database.rm.db', r'./Databases/database.db')
        else:
            print("An error occurred. The database is missing. Please re-download the project and try again.")
    else:
        print("An error occurred. The setup was already done before")

def write(host, port, hash_salt, admin_password_hash, password, Session_Secret_Key):
    configure="""
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
host = '%(host)s'    # Host setzen
threaded = True     # Multithreading erlaubt mehrere Clients gleichzeitig
port = '%(port)s'       # Port setzen

hash_salt = "%(hash_salt)s"  #  Your random hash salt
admin_pw_hash = "%(admin_password_hash)s"
# admin_pw_hash  = hashlib.sha512(bytes(<your_password> + hash_salt, "utf8")).hexdigest()
password = %(password)s # password for room_id
Session_Secret_Key = b'%(Session_Secret_Key)s'
    """ % {"host": host, "port": port , "hash_salt":hash_salt, "admin_password_hash":admin_password_hash, "password":password, "Session_Secret_Key":Session_Secret_Key}

    with open("./MyLibs/configure.py", "w") as file:
        file.write(configure)

if __name__ == "__main__":
    full_install()
