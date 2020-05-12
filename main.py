from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
from parse_utils import get_reviews, get_next_page, gd_login
from lxml import etree
from urllib.parse import urljoin
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

BASE_URL = 'http://www.glassdoor.com'
LOGIN_URL = 'https://www.glassdoor.com/profile/login_input.htm'
STARTING_PATH = "/Interview/Coursera-Interview-Questions-E654749.htm"


def main():

    # Launch driver
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # Log into account
    with open('secret.json') as f:
        secret_data = json.load(f)

    email = secret_data['email']
    pwd = secret_data['pwd']

    driver.get(LOGIN_URL)
    gd_login(driver, email, pwd)

    reviews = []
    next_page = STARTING_PATH

    while next_page:
        url = urljoin(BASE_URL, next_page)
        logger.info(f'Current page: {url}')
        driver.get(url)
        doc = etree.HTML(driver.page_source)
        data = get_reviews(doc)
        reviews.extend(data)
        next_page = get_next_page(doc)

    with open("reviews.json", "w") as f:
        json.dump(reviews, f, indent=4)

    driver.quit()


if __name__ == '__main__':
    main()
