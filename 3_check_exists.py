import os
import sqlite3

MAX_NAME_LENGTH = 40
base_folder = "Library"  # change if necessary

database = sqlite3.connect('main.db')

for video in database.execute("SELECT * FROM Videos WHERE file_exists IS NOT NULL"):
    dirs = []
    for i in range(4):
        dirs.append((video[i][0:MAX_NAME_LENGTH]).strip())

    directory = "{}/{}/{}".format(base_folder, dirs[0], dirs[2])
    path = "{}/{}.mp4".format(directory, dirs[3])

    if os.path.isfile(path):
        database.execute("UPDATE Videos SET file_exists = TRUE WHERE pageUrl = ?", [video[4]])
    else:
        database.execute("UPDATE Videos SET file_exists = FALSE WHERE pageURL = ?", [video[4]])

database.commit()
