from webdriver_manager.chrome import ChromeDriverManager
import json
from parse_utils import *
from lxml import etree
from urllib.parse import urljoin
import logging
import logging.config
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

BASE_URL = 'http://www.glassdoor.com'
LOGIN_URL = urljoin(BASE_URL, 'profile/login_input.htm')
DEFAULT_LOCATION = 'San Francisco, CA'
DELAY = 20

# Get the names of companies:
companies_list = []
with open('companies.json') as f:
    companies = json.load(f)

for comp in companies['companies'].split(','):
    companies_list.append(comp)


def main():

    # Launch driver
    chrome_options = webdriver.chrome.options.Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # Log into account
    with open('secret.json') as f:
        secrets = json.load(f)

    email = secrets['email']
    pwd = secrets['pwd']

    # Log into account
    gd_login(driver, LOGIN_URL, email, pwd)

    results = []

    for company in companies_list:
        try:
            element = WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//a[@href='/Reviews/index.htm']"))
            )
            element.click()
        except StaleElementReferenceException as e:
            print(e)
            pass

        # Enter location
        location_input = None
        try:
            location_input = WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@id='LocationSearch']"))
            )
        except TimeoutException:
            location_input = WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@id='sc.location']"))
            )
        finally:
            if location_input:
                enter_location(location_input, DEFAULT_LOCATION)
            else:
                logger.error(f'Not able to find location input element. Exiting...')
                driver.quit()
                return

        # Enter company name
        company_input = None
        try:
            company_input = WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@id='KeywordSearch']"))
            )
        except TimeoutException:
            company_input = WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@id='sc.keyword']"))
            )
        finally:
            if company_input:
                enter_company_name(company_input, company)
            else:
                logger.error(f'Not able to find keyword input element. Exiting...')
                driver.quit()
                return

        # Check if company page was opened
        try:
            WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//a[@class='eiCell cell interviews ']"))
            )
            company_url = driver.current_url
        except TimeoutException:
            doc = etree.HTML(driver.page_source)
            company_url = pick_company_from_search_results(doc, company)

        if company_url:
            company_url = urljoin(BASE_URL, company_url)
            logger.info(f'Current company URL: {company_url}')
            driver.get(company_url)
        else:
            logger.error(f'Not able to find company URL. Exiting...')
            continue
            #driver.quit()
            #return

        # Getting to interviews reviews
        try:
            interviews_link = WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//a[@class='eiCell cell interviews ']"))
            )
        except TimeoutException:
            logger.error(f'Not able to find interview reviews link. Exiting...')
            continue
            #driver.quit()
            #return

        first_page = interviews_link.get_attribute('href')
        driver.get(urljoin(BASE_URL, first_page))

        # Sorting reviews by date
        try:
            WebDriverWait(driver, DELAY).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@class='sorts']"))
            )
            driver.find_element_by_xpath(
                '//*[@class="sorts"]/option[2]').click()
        except StaleElementReferenceException as e:
            print(e)

        reviews = []
        cut_date = "2019-06-01"

        # Collect reviews from the first page
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@class=' empReview cf ']"))
            )
            doc = etree.HTML(driver.page_source)
            data, flag_stop = get_reviews(doc, company, cut_date)
            preprocess(data)
            reviews.extend(data)
            with open("reviews.json", "a") as f:
                json.dump(reviews, f, indent=4)

            for review in data:
                r = requests.post('https://gdreviews.herokuapp.com/api/reviews/', json=review)
                if r.status_code == 201:
                    logger.info(f"Success: {review['company']} - {review['role']}")
                else:
                    logger.error(f"Failure: {r.status_code} - {r.text} {review['company']}")
            if not flag_stop:
                next_page = get_next_page(doc)
            else:
                next_page = None

            logger.info(f'collected reviews from the first page: {driver.current_url}')
            print(next_page)
        except TimeoutException:
            logger.error(f'Not able to load interview reviews. Exiting...')
            continue
            #driver.quit()
            #return

        # Collect the rest of the reviews
        page = 1
        while next_page: # and page < pages:
            url = urljoin(BASE_URL, next_page)
            logger.info(f'Current page: {url}')
            driver.get(url)
            doc = etree.HTML(driver.page_source)
            data, flag_stop = get_reviews(doc, company, cut_date)
            preprocess(data)
            reviews.extend(data)

            with open("reviews.json", "a") as f:
                json.dump(reviews, f, indent=4)

            try:
                for review in data:
                    r = requests.post('https://gdreviews.herokuapp.com/api/reviews/', json=review)
                    if r.status_code == 201:
                        logger.info(f"Success: {review['company']} - {review['role']}")
                    else:
                        logger.error(f"Failure: {r.status_code} - {r.text} {review['company']}")
                if not flag_stop:
                    next_page = get_next_page(doc)
                    page += 1
                else:
                    next_page = None
            except ConnectionError:
                pass

        results.extend(reviews)
        logger.info(f'Finished with the {company}')

    driver.quit()


if __name__ == '__main__':
    main()
