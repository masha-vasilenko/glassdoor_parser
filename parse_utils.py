import logging
import logging.config
from lxml import etree
import time
import nltk
import string

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('parser')


def get_reviews(doc, company):
    results = []
    reviews = doc.cssselect("li.empReview.cf")
    get_role = etree.XPath(f".//span[{_klass('reviewer')}]/text()")
    get_date = etree.XPath(".//time/@datetime")
    get_helpful = etree.XPath(f".//span[{_klass('helpfulCount')}]/text()")
    get_outcomes = etree.XPath(f".//div[{_klass('interviewOutcomes')}]//span/text()")
    get_application = etree.XPath(f".//p[{_klass('applicationDetails')}]/text()")
    get_interview = etree.XPath(f".//p[{_klass('interviewDetails')}]/text()")
    get_questions = etree.XPath(f".//div[{_klass('interviewQuestions')}]//span[{_klass('interviewQuestion')}]/text()")

    for review in reviews:
        data = {
            'role': (get_role(review) or [None])[0],
            'date': (get_date(review) or [None])[0],
            'helpful': (get_helpful(review) or [None])[0],
            'outcomes': get_outcomes(review),
            'application': (get_application(review) or [None])[0],
            'details': (get_interview(review) or [None])[0],
            'questions': get_questions(review),
            'company': company,
        }
        results.append(data)
    return results


def _klass(klass):
    return f"contains(concat(' ',normalize-space(@class),' '),' {klass} ')"


def get_next_page(doc):
    paging_controls_expr = "//div[contains(concat(' ',normalize-space(@class),' '),' pagingControls ')]"
    next_elem_expr = "//li[contains(concat(' ',normalize-space(@class),' '),' next ')]"
    link_expr = "/a/@href"
    xpath_expr = paging_controls_expr + next_elem_expr + link_expr
    find = etree.XPath(xpath_expr)
    next_page_link = find(doc)
    return next_page_link[0] if next_page_link else None


def gd_login(driver, login_url, email, pwd):

    driver.get(login_url)
    email_field = driver.find_element_by_xpath(
        "//*[@type='submit']//preceding::input[2]"
    )
    email_field.send_keys(email)
    pwd_field = driver.find_element_by_xpath(
        "//*[@type='submit']//preceding::input[1]"
    )
    pwd_field.send_keys(pwd)
    pwd_field.submit()
    time.sleep(3)


def enter_company_name(element, company):
    element.clear()
    element.send_keys(company)
    element.submit()


def enter_location(element, location):
    element.clear()
    # element.send_keys(location)
    # element.submit()


def pick_company_from_search_results(doc, company):
    get_links = etree.XPath(f"//a[contains(@href, 'Overview')]")
    links = get_links(doc)
    best_link = None
    best_score = float('inf')
    for link in links:
        if link.text:
            score = get_word_distance(company.lower(), link.text.lower().strip())
            if score < best_score:
                best_link = link.attrib['href']
                best_score = score
    if best_link:
        return best_link.strip('/')


def get_word_distance(target, word):
    return nltk.edit_distance(target, word)


def preprocess(reviews):
    for review in reviews:
        try:
            review['helpful'] = int(''.join([c for c in review['helpful'] if c in string.digits]))
        except TypeError:
            review['helpful'] = None
        except ValueError:
            review['helpful'] = None

        try:
            review['accepted'] = review['outcomes'][0]
            review['experience'] = review['outcomes'][1]
            review['difficulty'] = review['outcomes'][2]
        except IndexError:
            review['accepted'] = ''
            review['experience'] = ''
            review['difficulty'] = ''

        questions_pr = []
        for question in review.get('questions', []):
            question_pr = {
                'question_text': question
            }
            questions_pr.append(question_pr)
        review['questions'] = questions_pr
