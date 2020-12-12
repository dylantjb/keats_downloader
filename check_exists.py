import os
import sqlite3
import subprocess

MAX_NAME_LENGTH = 40
base_folder = "Library"  # change if necessary

database = sqlite3.connect('main.db')

for video in database.execute("SELECT * FROM Videos WHERE file_exists = FALSE"):
    dirs = []
    for i in range(4):
        dirs.append((video[i][0:MAX_NAME_LENGTH]).strip())

    directory = "{}/{}/{}".format(base_folder, dirs[0], dirs[2])
    path = "{}/{}.mp4".format(directory, dirs[3])
    check_subs = 'ffmpeg -i "%s" -c copy -map 0:s -f null - -v 0 -hide_banner && echo true || echo false'

    if os.path.isfile(path) and subprocess.check_output(check_subs % path, shell=True, text=True).strip() == "true":
        database.execute("UPDATE Videos SET file_exists = TRUE WHERE pageUrl = ?", [video[4]])
    else:
        database.execute("UPDATE Videos SET file_exists = FALSE WHERE pageURL = ?", [video[4]])

database.commit()
