import os
import sqlite3
import subprocess
from pathlib import Path
from time import sleep

import ffmpeg

MAX_NAME_LENGTH = 40
base_folder = "Library"  # change path if necessary

database = sqlite3.connect('main.db')


def save():
    for video in database.execute("SELECT * FROM Videos WHERE videoUrl IS NOT NULL"):
        success = True
        dirs = []
        
        for i in range(4):
            dirs.append((video[i][0:MAX_NAME_LENGTH]).strip())

        directory = "{}/{}/{}".format(base_folder, dirs[0], dirs[2])
        path = "{}/{}.mp4".format(directory, dirs[3])

        if os.path.isfile(path):
            check_subs = 'ffmpeg -i "%s" -c copy -map 0:s -f null - -v 0 -hide_banner && echo true || echo false'
            if subprocess.check_output(check_subs % path, shell=True, text=True) == "false" and video[6] is not None:
                os.remove(path)
            else:
                continue

        print(video[1], video[2], video[3])
        Path(directory).mkdir(parents=True, exist_ok=True)

        try:  # Tries to convert m3u8 from url to mp4
            if video[6] is None:
                ffmpeg.input(video[5]).output(path, codec="copy").run()
            else:
                (
                    ffmpeg
                    .input(video[5])
                    .output(path, vcodec="copy", acodec="copy", scodec="mov_text",
                            **{'metadata:s:s:0': "language=eng", 'disposition:s:s:0': "default"})
                    .global_args('-i', video[6])
                    .run()
                )
        except:  # Connection lost // Video URLs expire every few hours so if you get a http status code 404 in
            # stderr then you need to run get_video_urls.py again as a refresh
            sleep(10)
            success = False
            os.remove(path)
            break

    if not success:
        save()


save()
