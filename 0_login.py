from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=selenium/chrome_driver")
driver = webdriver.Chrome(executable_path="selenium/chromedriver", options=options)  # for Windows add .exe

driver.get("https://keats.kcl.ac.uk/")

print("Close chrome browser when finished")
