from builtins import iter

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import nltk
import string

#DONE: add finding the best match



def fetch(url, driver):
    time.sleep(3)
    driver.get(url)
    return driver.page_source


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def get_word_distance(target, word):
    return nltk.edit_distance(target, word)


def get_to_company_search_page(driver):
    """ Getting to the company search page"""

    time.sleep(3)

    companies_button = driver.find_element_by_xpath('//*[contains(@href,"/Reviews/index.htm")]//h3[@class="mx-xsm"]')
    companies_button.click()


def get_to_company_interviews_page(driver):
    """ Getting to the company search page"""
    time.sleep(3)

    interviews_button = driver.find_element_by_xpath('//a[@class="eiCell cell interviews "]')
    interviews_button.click()


def enter_company_name(driver, company):
    """Enter the name of the company"""
    try:
        comp_search_field = driver.find_element_by_xpath('//input[@class="keyword"]')
    except NoSuchElementException:
        comp_search_field = driver.find_element_by_xpath('//input[@name="sc.keyword"]')
    #comp_search_field = driver.find_element_by_xpath('//*[@type="submit"]//preceding::input[2]')
    comp_search_field.clear()
    comp_search_field.send_keys(company)
    comp_search_field.submit()


def enter_location(driver, location):
    try:
        location_search_field = driver.find_element_by_xpath('//input[@id="LocationSearch"]')
    except NoSuchElementException:
        location_search_field = driver.find_element_by_xpath('//div[@class="css-q444d9"]//input[@id="sc.location"]')
    #location_search_field = driver.find_element_by_xpath('//*[@type="submit"]//preceding::input[1]')
    location_search_field.clear()
    location_search_field.send_keys(location)
    location_search_field.submit()

def get_company_page_url(driver, target_company):
    if check_exists_by_xpath(driver, '//*[contains(text(),"Showing results for")]'):
        # If the search redirects to a company search page
        company_search_links = {}
        for link in driver.find_elements_by_xpath('//*[contains(@href,"/Overview/Working-at")]'):
            if link.text != '' and 'Logo' not in link.text:
                company_search_links[link.text] = link.get_attribute('href')
        clean_company_search_links = {}
        for company, link in company_search_links.items():
            clean_company_search_links[''.join([w.lower().strip() for w in company if w not in string.punctuation])] = [
                link]

        # Distance
        for company in clean_company_search_links.keys():
            edit_dist = get_word_distance(target_company, company)
            clean_company_search_links[company].append(edit_dist)

        # Sorting by scores
        results = {k: v for k, v in sorted(clean_company_search_links.items(), key=lambda item: item[1][1])}
        match = next(iter(results.items()))[1][0]  # get the link to the company page
        return match

    else:
        company_url = driver.current_url
        return company_url





