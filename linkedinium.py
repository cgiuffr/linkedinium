#!/usr/bin/python3

from googlesearch import search

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse
import sys

name = "name"
affiliation = "affiliation"
username="user"
password="pass"
message="Hi!"

linkedin = "site:linkedin.com"
results = search("intitle:\"%s\" \"%s\" %s" % (name, affiliation, linkedin), num_results=1)
if len(results) == 0:
    results = search("%s \"%s\" %s" % (name, affiliation, linkedin), num_results=1)
if len(results) == 0:
    sys.exit(1)
url = results[0]
print(url)

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.linkedin.com/login")
elem = driver.find_element_by_id("username")
elem.clear()
elem.send_keys(username)
elem = driver.find_element_by_id("password")
elem.clear()
elem.send_keys(password)
elem.send_keys(Keys.RETURN)

driver.get(url)
elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="Connect"]')))
try:
  elem = driver.find_element_by_xpath('//span[text()="More actions"]/ancestor::button')
  elem.click()
except:
  pass
elem = driver.find_element_by_xpath('//span[text()="Connect"]')
elem.click()
elem = driver.find_element_by_xpath('//span[text()="Add a note"]')
elem.click()
elem = driver.find_element_by_name("message")
elem.clear()
elem.send_keys(message)
elem = driver.find_element_by_xpath('//span[text()="Cancel"]')
elem.click()
driver.close()