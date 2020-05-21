from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
from parse_utils import get_reviews, get_next_page, gd_login
from lxml import etree
from urllib.parse import urljoin
import logging
import logging.config
from navigation import *

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

BASE_URL = 'http://www.glassdoor.com'
LOGIN_URL = 'https://www.glassdoor.com/profile/login_input.htm'
#STARTING_PATH = "/Interview/Coursera-Interview-Questions-E654749.htm"
LOGIN_URL = 'https://www.glassdoor.com/profile/login_input.htm'
#COMPANY= 'aetna'
LOCATION = 'San Francisco, CA'
companies_list = ['stripe', 'coursera']

def main():

    # Launch drivers
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_argument("--headless")

    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver = webdriver.Chrome(ChromeDriverManager().install())


    # Log into account
    with open('secret.json') as f:
        secret_data = json.load(f)

    email = secret_data['email']
    pwd = secret_data['pwd']

    # Log into account
    gd_login(driver, LOGIN_URL, email, pwd)

    # Navigate to a company search page
    get_to_company_search_page(driver)
    # Enter location
    enter_location(driver, LOCATION)

    for company in companies_list:

        # Enter company name
        enter_company_name(driver, company)
        #enter_location(driver, LOCATION)
        # Get the company link
        time.sleep(3)
        company_url = get_company_page_url(driver, company)
        print(company_url)
        driver.get(company_url)
        get_to_company_interviews_page(driver)

        next_page = driver.current_url

        #Collect reviews
        reviews = []
        while next_page:
            url = urljoin(BASE_URL, next_page)
            logger.info(f'Current page: {url}')
            driver.get(url)
            doc = etree.HTML(driver.page_source)
            data = get_reviews(doc)
            reviews.extend(data)
            next_page = get_next_page(doc)

        with open("reviews_%s.json" % company, "w") as f:
             json.dump(reviews, f, indent=4)

    driver.quit()

if __name__ == '__main__':
    main()
