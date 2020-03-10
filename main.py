import selenium
from selenium import webdriver
import json


def main():
    print(selenium.__version__)


def gd_login(driver, email, pwd):
    userfield = driver.find_element_by_id("userEmail")
    userfield.send_keys(email)
    pwdfield = driver.find_element_by_id("userPassword")
    pwdfield.send_keys(pwd)
    pwdfield.submit()


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


# Quit the driver
driver.quit()


if __name__ == '__main__':
    main()
