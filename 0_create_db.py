import sqlite3

statement = "CREATE TABLE \"Videos\" ( `course` TEXT NOT NULL, `courseID` TEXT NOT NULL, `week` TEXT NOT NULL, " \
            "`name` TEXT NOT NULL, `pageUrl` TEXT NOT NULL UNIQUE, `videoUrl` TEXT, `srtUrl` TEXT, `file_exists` " \
            "BOOLEAN DEFAULT FALSE, PRIMARY KEY(`pageUrl`) )"

database = sqlite3.connect("main.db")
database.execute(statement)
database.commit()
