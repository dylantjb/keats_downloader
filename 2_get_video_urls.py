import sqlite3
from time import sleep

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver

database = sqlite3.connect('main.db')

options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=selenium/chrome_driver")  # add .exe for Windows
options.add_argument("disable-web-security")
driver = webdriver.Chrome(executable_path="selenium/chromedriver", options=options)

driver.get("https://keats.kcl.ac.uk/")
wait_element = ec.presence_of_element_located((By.ID, 'page-footer'))
WebDriverWait(driver, 10).until(wait_element)

for video in database.execute("SELECT * FROM Videos WHERE file_exists = 0"):
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
        except:
            print("Failed to find video url")
            continue

        video_src = video_tag.get_attribute('src')

        # Checks if video url is working or it reloads
        if requests.get(video_src).status_code == 404:
            continue

        try:  # Tries to find the child class where subs are
            srt = video_tag.find_element_by_xpath("./child::*").get_attribute('src')
            print("srt found")
        except:
            srt = None

        database.execute("UPDATE Videos SET videoUrl=?, srtUrl=? WHERE pageUrl=?", (video_src, srt, video[4]))
        database.commit()
        break

driver.close()
