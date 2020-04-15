from bs4 import BeautifulSoup
import sys


# DONE: Refactor parse_html, consider splitting into smaller functions
# DONE: Think about try..except, does it really protect from failing, also except should catch particular case
# TODO: Add to reviews: date, helpful score

def get_soup(html):
    soup = BeautifulSoup(html, features="html.parser")
    return soup


def get_role(review):
    "Get the role fo whic an applicant interviewed to"

    data_collected = {"role": None}
    role = review.select("h2.summary.strong.noMargTop.tightTop.margBotXs")[0]
    data_collected["role"] = role.text
    return data_collected


def get_impressions_from_review(review):
    '''Given the soup element review
    collect impressions data:
      offer - whether an offer was given,
      impression - overall impression from an interview (Neg, Pos, Neutral)
      difficulty - difficulty of an interview '''
    data_collected = {"offer": None, "impression": None, "interview_difficulty": None}

    outcomes = review.select(".interviewOutcomes")
    for out in outcomes:
        middle_panel = out.select(".middle")
        line = []
        for elem in middle_panel:
            if list((elem.select("span", class_="middle"))):
                el = elem.select("span", class_="middle")[0].text
                # print(el)
                line.append(el)
        if "Offer" in line[0]:
            data_collected["offer"] = line[0]
        else:
            data_collected["offer"] = ""

        if "Experience" in line[1]:
            data_collected["impression"] = line[1]
        else:
            data_collected["impression"] = ""

        if "Interview" in line[2]:
            data_collected["interview_difficulty"] = line[2]
        else:
            data_collected["interview_difficulty"] = ""
    return data_collected


def get_interview_application_process(review):
    "Given the soup element review, return the info about application process "

    data_collected = {"application": None}
    if review.select("p.applicationDetails.continueReading")[0]:
        application = review.select("p.applicationDetails.continueReading")[0]
        data_collected["application"] = application.text
    else:
        data_collected["application"] = ""
    return data_collected


def get_interview_details(review):
    "Given the soup element review, return the info about application process "

    data_collected = {"interview": None}

    if review.select("p.interviewDetails.continueReading")[0]:
        interview = review.select("p.interviewDetails.continueReading")[0]
        data_collected["interview"] = interview.text
    else:
        data_collected["interview"] = ""
    return data_collected


def get_interview_questions(review):
    data_collected = {"interview_questions": None}

    if review.select(".interviewQuestion.noPadVert.truncateThis.wrapToggleStr")[0]:
        questions = review.select(".interviewQuestion.noPadVert.truncateThis.wrapToggleStr")[0]
        data_collected["interview_questions"] = questions.text
    else:
        data_collected["interview_questions"] = ""

    return data_collected


def parse_html(soup):
    """Parse HTML page and collect the reviews"""

    # Get roles to which reviewers applied
    final_results = []
    for review in soup.select("li.empReview.cf"):
        data_collected = {}
        # Get role
        data_collected.update(get_role(review))

        # Impressions
        data_collected.update(get_impressions_from_review(review))

        # Interview Application
        data_collected.update(get_interview_application_process(review))

        # Interview Details
        data_collected.update(get_interview_details(review))

        # Interview Questions
        data_collected.update(get_interview_questions(review))

        # Date of the review

        final_results.append(data_collected)

    return final_results


def get_next_page(soup):
    """Get the next page with reviews to parse"""
    next_page = None
    disabled = 0
    for l in soup.find_all(class_="next"):
        try:
            for dis in l.find_all(class_="disabled"):
                disabled = len(dis.text)
                next_page = None
        except:
            pass
        if disabled == 0:
            for link in l.find_all("a"):
                next_page = link.get('href')
                next_page = "http://www.glassdoor.com" + next_page.strip()
        else:
            next_page = None
    return next_page
