#!/usr/bin/python3

from googlesearch import search

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse
import sys
import re
import params

def LIProfileURLFromName(name, affiliation):
  linkedin = "site:linkedin.com"
  results = search("intitle:\"%s\" \"%s\" %s" % (name, affiliation, linkedin), num_results=1)
  if len(results) == 0:
      results = search("%s \"%s\" %s" % (name, affiliation, linkedin), num_results=1)
  if len(results) == 0:
      return None
  url = results[0]
  return url

def LILogin(driver, username, password):
  driver.get("https://www.linkedin.com/login")
  elem = driver.find_element_by_id("username")
  elem.clear()
  elem.send_keys(username)
  elem = driver.find_element_by_id("password")
  elem.clear()
  elem.send_keys(password)
  elem.send_keys(Keys.RETURN)

def LIProfileLoad(driver, pURL):
  driver.get(pURL)
  WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'dist-value')))
  name = re.compile('[^\s]*\s(.*)\s.\sLinkedIn').match(driver.title).group(1)
  elem = driver.find_element_by_class_name("dist-value")

  return name, elem.text

def LIProfileConnect(driver, name, message):
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
  elem = driver.find_element_by_xpath('//span[text()="Send"]')
  #elem.click()
  print('CONNECT: ' + name)

def LIGroupLoad(driver, gURL):
  driver.get(gURL)
  WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//span[text()="Invite connections"]')))
  return

def LIGroupInvite(driver, name):
  elem = driver.find_element_by_xpath('//span[text()="Invite connections"]/ancestor::button')
  elem.click()
  elem = driver.find_element_by_xpath('//*[@id="-invitee-picker-search"]//input')
  elem.click()
  elem.send_keys(name)
  elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[text()="%s"]' % name)))
  if driver.find_elements_by_xpath('//div[text()="Member"]'):
    print('ALREADY INVITED: ' + name)
    return
  elem.click()
  elem = driver.find_element_by_xpath('//span[text()="Invite 1"]/ancestor::button')
  #elem.click()
  print('GROUP INVITE: ' + name)

  return

#
# main()
#

try:
    import params
except ImportError:
    print("Please create params.py based on params_default.py first.")
    sys.exit(1)

driver = webdriver.Chrome()
driver.maximize_window()

LILogin(driver, params.username, params.password)

for name in params.names:
  pURL = LIProfileURLFromName(name, params.affiliation)
  
  name, distance = LIProfileLoad(driver, pURL)
  
  if distance != '1st':
    LIProfileConnect(driver, name, params.connect_message)
  else:
    LIGroupLoad(driver, params.group)
    LIGroupInvite(driver, name)

driver.close()