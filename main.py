import selenium
from selenium import webdriver
import json
import time
import random




def main():
    print(selenium.__version__)


def gd_login(driver, email, pwd):
    #Given the driver and credentials, login

    userfield = driver.find_element_by_id("userEmail")
    userfield.send_keys(email)
    pwdfield = driver.find_element_by_id("userPassword")
    pwdfield.send_keys(pwd)
    pwdfield.submit()


def fetch(url, driver, delay =(1,3)):
    """Simulate random human clicking
    Fetch the page source and return html object"""

    time.sleep(random.randint(delay[0],delay[1]))
    driver.get(url)
    html = driver.page_source
    return html

DRIVER_PATH = '/usr/local/bin/chromedriver'
LOGIN_URL = 'https://www.glassdoor.com/profile/login_input.htm'


# Loading email and password from secret.json
with open('secret.json') as f:
    secret_data = json.load(f)

email = secret_data['email']
pwd = secret_data['pwd']

#Launch driver
driver = webdriver.Chrome(DRIVER_PATH)
driver.get(LOGIN_URL)
driver.implicitly_wait(100)

# Log into account
gd_login(driver,email,pwd)


#print(type(html))
URL_TO_FETCH = "https://www.glassdoor.com/Interview/Coursera-Interview-Questions-E654749.htm"
html = fetch(URL_TO_FETCH, driver)

with open("result.html", "w") as file:
   file.write(html)

# Quit the driver
driver.quit()


if __name__ == '__main__':
    main()
