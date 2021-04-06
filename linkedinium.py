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
import unicodedata
import params

def LIProfileURLFromNameViaGoogle(name, affiliation, affiliation_extra):
  linkedin = "site:linkedin.com"
  results = search("intitle:\"%s\" \"%s\" %s" % (name, affiliation, linkedin), num_results=1)
  if len(results) == 0:
      results = search("%s \"%s\" %s" % (name, affiliation, linkedin), num_results=1)
  if len(results) == 0:
      return None
  url = results[0]
  return url

def LIProfileURLFromNameViaLI(driver, name, affiliation, affiliation_extra):
  if affiliation_extra:
    ret = LIProfileURLFromNameViaLISearch(driver, name + ' ' + affiliation + ' ' + affiliation_extra)
    if ret:
      return ret
  return LIProfileURLFromNameViaLISearch(driver, name + ' ' + affiliation)

def LIProfileURLFromNameViaLISearch(driver, search_string):
  driver.get('https://www.linkedin.com/feed/')
  elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"]')))
  elem.click()
  elem.clear()
  elem.send_keys(search_string)
  elem.send_keys(Keys.ENTER)
  WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="search-results-container"]//span[text()="Edit search" or text()="Message" or text()="Connect" or text()="Follow" or text()="Pending"]')))

  elems = driver.find_elements_by_xpath('//span[text()="Edit search"]')
  if elems:
    print('[%s] PROFILE: None' % name)
    return None
  elems = driver.find_elements_by_xpath('//a[contains(@href, "https://www.linkedin.com/in/")]')
  assert elems
  urls = []
  match_urls = []
  for elem in elems:
    name_elems = elem.find_elements_by_xpath('.//span[@dir="ltr"]/span')
    if not name_elems or len(name_elems)>2:
      continue
    url = elem.get_attribute('href')
    cmp_name = unicodedata.normalize('NFKD', name_elems[0].text)
    cmp_name = cmp_name.encode('ascii', 'ignore').decode('ascii', 'ignore').strip()
    if cmp_name.lower() == name.lower():
      match_urls.append(url)
      continue
    urls.append(url)
  if len(match_urls) == 1:
    url = match_urls[0]
    print('[%s] PROFILE: OK - %s' % (name, url))
    return url
  if len(match_urls) > 1 or len(urls) > 1:
    print('[%s] PROFILE: Many - (%s)' % (name, ', '.join(match_urls) + ', '.join(urls)))
    return None
  url = urls[0]
  print('[%s] PROFILE: OK - %s' % (name, url))
  return url

def LIProfileURLFromName(driver, name, affiliation, affiliation_extra, use_google):
  if use_google:
    return LIProfileURLFromNameViaGoogle(name, affiliation, affiliation_extra)
  else:
    return LIProfileURLFromNameViaLI(driver, name, affiliation, affiliation_extra)

def LILogin(driver, username, password):
  driver.get("https://www.linkedin.com/login")
  elem = driver.find_element_by_id("username")
  elem.clear()
  elem.send_keys(username)
  elem = driver.find_element_by_id("password")
  elem.clear()
  elem.send_keys(password)
  elem.send_keys(Keys.RETURN)
  WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"]')))

def LIProfileLoad(driver, pURL):
  driver.get(pURL)
  elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'dist-value')))
  name = re.compile('^[^\s]*\s(.*)\s.\sLinkedIn$').match(driver.title).group(1)

  status = "not-connected"
  if elem.text == "1st":
    status = "connected"
  elif driver.find_elements_by_xpath('//span[text()="Pending"]'):
    status = "pending"
  print('[%s] PROFILE LOAD: %s' % (name, status))

  return name, status

def LIProfileConnect(driver, name, status, message, dry_run):
  if status == "connected":
    return True
  if status == "pending":
    return False
  if dry_run:
    print('[%s] CONNECT: Dry run' % name)
    return False

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
  elem.click()
  print('[%s] CONNECT: OK' % name)

  return False

def LIGroupLoad(driver, gURL):
  driver.get(gURL)
  WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//span[text()="Invite connections"]')))
  return

def LIGroupInvite(driver, name, dry_run):
  if dry_run:
    print('[%s] INVITE: Dry run' % name)
    return
  elem = driver.find_element_by_xpath('//span[text()="Invite connections"]/ancestor::button')
  elem.click()
  elem = driver.find_element_by_xpath('//*[@id="-invitee-picker-search"]//input')
  elem.click()
  elem.clear()
  elem.send_keys(name)
  elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[text()="%s"]' % name)))
  if driver.find_elements_by_xpath('//div[text()="Member"]'):
    print('[%s] INVITE: Member' % name)
    return
  if driver.find_elements_by_xpath('//div[text()="Invited"]'):
    print('[%s] INVITE: Pending' % name)
    return
  elem.click()
  elem = driver.find_element_by_xpath('//span[text()="Invite 1"]/ancestor::button')
  elem.click()
  print('[%s] INVITE: OK' % name)

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
  pURL = LIProfileURLFromName(driver, name, params.affiliation, params.affiliation_extra, params.use_google)
  if not pURL:
    continue
  
  name, status = LIProfileLoad(driver, pURL)
  
  if LIProfileConnect(driver, name, status, params.connect_message, params.connect_dry_run):
    LIGroupLoad(driver, params.group)
    LIGroupInvite(driver, name, params.invite_dry_run)

driver.close()