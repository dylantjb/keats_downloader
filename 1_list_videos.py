from os import getcwd
import sqlite3

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver
from chromedriver_py import binary_path

with open("courses.txt", "r") as f:
    courses = [line.strip() for line in f.readlines()]

database = sqlite3.connect('main.db')

options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("--user-data-dir=" + getcwd() + "/.userdata")
options.add_argument("--disable-web-security")
driver = webdriver.Chrome(executable_path=binary_path, options=options)

driver.get("https://keats.kcl.ac.uk/")
wait_element = ec.presence_of_element_located((By.ID, 'page-footer'))
WebDriverWait(driver, 10).until(wait_element)

for course in courses:
    driver.get(course)
    print(course)
    WebDriverWait(driver, 10).until(wait_element)
    video_dicts = driver.execute_script(open("utils/list_videos.js").read())
    videos = []

    video_index = 1
    weekOfPreviousVideo = ""
    for video in video_dicts:
        if video["week"] != weekOfPreviousVideo:
            video_index = 1
            weekOfPreviousVideo = video["week"]
        video["name"] = "{:02}_{}".format(video_index, video["name"])
        videos.append(
            (
                video["course"],
                video["courseID"],
                video["week"],
                video["name"],
                video["pageUrl"],
            )
        )
        video_index += 1

    database.executemany(
        "INSERT INTO Videos (course, courseID, week, name, pageUrl) VALUES (?, ?, ?, ?, ?) ON CONFLICT(pageUrl) DO UPDATE SET courseID=courseID",
        videos)

database.commit()
driver.close()
