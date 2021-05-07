import sqlite3
from os import getcwd,environ
from pathlib import Path
import ffmpeg
from time import sleep

from utils.show_progress import Progress

from selenium import webdriver
from chromedriver_py import binary_path
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


database = sqlite3.connect('main.db')
MAX_NAME_LENGTH = 40
base_folder = environ["HOME"] + "/Videos/Lectures"  # change if necessary

options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=" + getcwd() + "/.userdata")
options.add_argument("--disable-web-security")
driver = webdriver.Chrome(executable_path=binary_path, options=options)  # add .exe for Windows

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

        Path(directory).mkdir(parents=True, exist_ok=True)

        try:
            Progress(video_url, path, srt_url).run()
        except ffmpeg.Error:  # Connection lost or invalid url
            sleep(10)
            return True


for video in database.execute("SELECT * FROM Videos WHERE file_exists = FALSE"):
    print(video[1], video[2], video[3])

    while True:
        try:
            driver.get(video[4])
        except WebDriverException:
            sleep(10)
            continue

        # Wait and open contentFrame
        try:
            WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.ID, "contentframe"))
            )
        except:
            # The only known case of failure is when a video has been removed
            print("Failed to find frame")
            continue
        driver.switch_to.frame(driver.find_element_by_id("contentframe"))

        # Make sure that the player is loaded
        driver.execute_script(open("utils/create_player.js").read())
        # Process player
        try:
            WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.ID, "kplayer_ifp"))
            )
        except:
            # Despite the create_player script the player still wasn't found
            print("Failed to load player")
            continue

        driver.switch_to.frame(driver.find_element_by_id("kplayer_ifp"))

        # Artificial wait for the contents of kplayer_ifp
        sleep(1)

        try:  # Try and find the class where the video is
            video_tag = driver.find_element_by_tag_name("video")
        except NoSuchElementException:
            print("Failed to find video class")
            continue

        video_url = video_tag.get_attribute("src")
        if not video_url:
            print("Failed to find video source")
            break

        try:  # Tries to find the child class where subs are
            srt_url = video_tag.find_element_by_xpath("./child::*").get_attribute("src")
            print("srt found")
        except NoSuchElementException:
            srt_url = None

        if save(video_url, srt_url, video[4]):
            continue
        break

database.close()
driver.close()
