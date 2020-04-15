from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from parse_html import *

LOGIN_URL = 'https://www.glassdoor.com/profile/login_input.htm'
URL_TO_FETCH = "https://www.glassdoor.com/Interview/Coursera-Interview-Questions-E654749.htm"

# TODO: Use logger instead of print statements



def main():
    with open('secret.json') as f:
        secret_data = json.load(f)

    email = secret_data['email']
    pwd = secret_data['pwd']

    # Launch driver
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Log into account
    driver.get(LOGIN_URL)
    gd_login(driver, email, pwd)

    reviews = []
    next_page = URL_TO_FETCH

    while next_page:
        driver.get(next_page)
        html = driver.page_source
        soup = get_soup(html)
        reviews.extend(parse_html(soup))
        next_page = get_next_page(soup)

    with open("reviews.json", "w") as f:
        json.dump(reviews, f, indent=4)

    # Quit the driver
    driver.quit()


def gd_login(driver, email, pwd):
    # Given the driver and credentials, login
    email_field = driver.find_element_by_xpath(
        "//div[@class=' css-1ohf0ui']//div[@class='css-q444d9']//input[1]"
    )
    email_field.send_keys(email)
    pwd_field = driver.find_element_by_xpath(
        "//div[@class='mt-xsm']//div[@class=' css-1ohf0ui']//div[@class='css-q444d9']//input[1]"
    )
    pwd_field.send_keys(pwd)
    pwd_field.submit()
    time.sleep(3)


def fetch(url, driver):
    driver.get(url)
    return driver.page_source


if __name__ == '__main__':
    main()
