from MyLibs import db, configure
import sqlite3 as sql

con = sql.connect(db.database)
cur = con.cursor()


with open("questions.txt",encoding='utf8') as file:
    for line in file.readlines():
        
        cur.execute("INSERT INTO questions(question) values('" + str(line) + "')")
        con.commit()

con.close()