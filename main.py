import selenium
from selenium import webdriver
import json

import requests
import time
import random
from bs4 import BeautifulSoup


def main():
    print(selenium.__version__)


def gd_login(driver, email, pwd):
    userfield = driver.find_element_by_id("userEmail")
    userfield.send_keys(email)
    pwdfield = driver.find_element_by_id("userPassword")
    pwdfield.send_keys(pwd)
    pwdfield.submit()


def fetch(url, delay =(1,3)):
    """Simulate random human clicking
    Fetch the page source and return html object"""

    time.sleep(random.randint(delay[0],delay[1]))
    try:
        response = requests.get(url, headers={'User-Agent': "Resistance is futile"})
    except ValueError as e:
        print(str(e))
        return '',BeautifulSoup('','html.parser')
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    return (html,soup)

driver_path = '/usr/local/bin/chromedriver'
login_url = 'https://www.glassdoor.com/profile/login_input.htm'

# Loading email and password from secret.json
with open('secret.json') as f:
    secret_data = json.load(f)

email = secret_data['email']
pwd = secret_data['pwd']

# Launch web driver
driver = webdriver.Chrome(driver_path)
driver.get(login_url)
driver.implicitly_wait(100)

# Log into account
gd_login(driver, email, pwd)

html,soup = fetch("https://www.glassdoor.com/Interview/Coursera-Interview-Questions-E654749.htm")

#print(type(html))

with open("result.html", "w") as file:
    file.write(html)

# Quit the driver
driver.quit()


if __name__ == '__main__':
    main()
