from os import getcwd
from selenium import webdriver
from chromedriver_py import binary_path

options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=" + getcwd() + "/.userdata")
driver = webdriver.Chrome(executable_path=binary_path, options=options)  # for Windows add .exe

driver.get("https://keats.kcl.ac.uk/")

print("Close chrome browser when finished")
