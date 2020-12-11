import sqlite3

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver

with open("courses.txt", "r") as f:
    courses = [line.strip() for line in f.readlines()]

print(courses)

database = sqlite3.connect('main.db')
# data_cursor = database.cursor()

options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=selenium/chrome_driver")
options.add_argument("disable-web-security")
driver = webdriver.Chrome(executable_path="selenium/chromedriver", options=options)

driver.get("https://keats.kcl.ac.uk/")
wait_element = ec.presence_of_element_located((By.ID, 'page-footer'))
WebDriverWait(driver, 10).until(wait_element)
for course in courses:
    driver.get(course)
    WebDriverWait(driver, 10).until(wait_element)
    videoDicts = driver.execute_script(open("list_videos.js").read())
    videos = []
    for video in videoDicts:
        # print(video)
        videos.append((video['course'], video['courseID'], video['week'], video['name'], video['pageUrl']))
    database.executemany(
        "INSERT INTO Videos (course, courseID, week, name, pageUrl) VALUES (?, ?, ?, ?, ?) ON CONFLICT(pageUrl) DO UPDATE SET courseID=courseID",
        videos)

database.commit()
driver.close()
