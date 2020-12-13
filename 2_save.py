import os
import sqlite3
from pathlib import Path
from time import sleep

from progress_bar import Progress

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


database = sqlite3.connect('main.db')
MAX_NAME_LENGTH = 40
base_folder = "Library"  # change if necessary

options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("--user-data-dir=" + os.getcwd() + "/selenium/chrome_driver")
options.add_argument("--disable-web-security")
driver = webdriver.Chrome(executable_path="selenium/chromedriver", options=options)  # add .exe for Windows
driver.get("https://keats.kcl.ac.uk/")
wait_element = ec.presence_of_element_located((By.ID, 'page-footer'))
WebDriverWait(driver, 10).until(wait_element)


def save(video_url, srt_url, page_url):
    for result in database.execute("SELECT * FROM Videos WHERE pageUrl=?", [page_url]):
        dirs = []
        for i in range(4):
            dirs.append((result[i][0:MAX_NAME_LENGTH]).strip())

        directory = "{}/{}/{}".format(base_folder, dirs[0], dirs[2])
        path = "{}/{}.mp4".format(directory, dirs[3])

        if os.path.isfile(path):
            if srt_url:
                os.remove(path)
            else:
                return

        Path(directory).mkdir(parents=True, exist_ok=True)

        try:
            Progress(video_url, path, srt_url).run()
            if srt_url:
                database.execute("UPDATE Videos SET file_exists = TRUE WHERE pageUrl = ?", [page_url])
                database.commit()
        except:  # Connection lost
            sleep(10)
            os.remove(path) if os.path.exists(path) else None
            return True


for video in database.execute("SELECT * FROM Videos WHERE file_exists = FALSE"):
    print(video[1], video[2], video[3])

    while True:
        try:  # Loads the video player before continuing
            driver.get(video[4])
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'contentframe')))
            driver.switch_to.frame(driver.find_element_by_id('contentframe'))
            driver.execute_script(open("create_player.js").read())
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'kplayer_ifp')))
            driver.switch_to.frame(driver.find_element_by_id('kplayer_ifp'))
            sleep(2)
        except:  # Connection lost
            sleep(10)
            continue

        try:  # Try and find the class where the video is
            video_tag = driver.find_element_by_tag_name('video')
        except exceptions.NoSuchElementException:
            print("Failed to find video frame")
            continue

        video_url = video_tag.get_attribute('src')
        if not video_url:
            print("Failed to find video url")
            break

        try:  # Tries to find the child class where subs are
            srt_url = video_tag.find_element_by_xpath("./child::*").get_attribute('src')
            print("srt found")
        except exceptions.NoSuchElementException:
            srt_url = None

        if save(video_url, srt_url, video[4]):
            continue
        break
