import selenium
from selenium import webdriver
import json
import time
import random
from parse_html import *




def main():
    print(selenium.__version__)


def gd_login(driver, email, pwd):
    #Given the driver and credentials, login

    #userfield = driver.find_element_by_id("userEmail")
    userfield = driver.find_element_by_xpath("//div[@class=' css-1ohf0ui']//div[@class='css-q444d9']//input[1]")
    userfield.send_keys(email)
    pwdfield = driver.find_element_by_xpath("//div[@class='mt-xsm']//div[@class=' css-1ohf0ui']//div[@class='css-q444d9']//input[1]")
    pwdfield.send_keys(pwd)
    pwdfield.submit()


def fetch(url, driver, delay =(1,3)):
    """Simulate random human clicking
    Fetch the page source and return html object"""

    #time.sleep(random.randint(delay[0],delay[1]))
    driver.implicitly_wait(250)
    driver.get(url)
    html = driver.page_source
    return html

DRIVER_PATH = '/usr/local/bin/chromedriver'
LOGIN_URL = 'https://www.glassdoor.com/profile/login_input.htm'


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
driver.implicitly_wait(100)


#print(type(html))
URL_TO_FETCH = "https://www.glassdoor.com/Interview/Coursera-Interview-Questions-E654749.htm"
html = fetch(URL_TO_FETCH, driver)


with open("result.html", "w") as file:
   file.write(html)

soup = get_soup(html)
print(len(soup))

interview_reviews = parse_html(soup)
next_page =get_next_page(soup)
print(next_page)

while next_page != None:
    driver.implicitly_wait(100)
    driver.get(next_page)
    html = driver.page_source
    soup = get_soup(html)
    interview_reviews.append(parse_html(soup))
    next_page=get_next_page(soup)

with open("interview_reviews.json", "w") as fp:
    json.dump(interview_reviews, fp)
# Quit the driver
driver.quit()



if __name__ == '__main__':
    main()
