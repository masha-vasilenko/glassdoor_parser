from bs4 import BeautifulSoup

with open('result.html') as f:
    html = f.read()

def get_soup(html):
    soup = BeautifulSoup(html, features="html.parser")
    return soup

def parse_html(soup):
    """Parse HTML page and collect the reviews"""

    # Get roles to which reviewers applied
    final_results = []
    for review in soup.select("li.empReview.cf"):
        data_collected = {"role": [], "offer": None, "impression": None, "interview_difficulty": None,
                          "application": None, "interview": None, "interview_questions": None}
        # Get role
        role = review.select("h2.summary.strong.noMargTop.tightTop.margBotXs")[0]
        data_collected["role"] = role.text

        # Impressions
        outcomes = review.select(".interviewOutcomes")
        for out in outcomes:
            middle_panel = out.select(".middle")
            line = []
            for elem in middle_panel:
                if list((elem.select("span", class_="middle"))) != []:
                    el = elem.select("span", class_="middle")[0].text
                    # print(el)
                    line.append(el)
            try:
                if "Offer" in line[0]:
                    data_collected["offer"] = line[0]
            except:
                pass
            try:
                if "Experience" in line[1]:
                    data_collected["impression"] = line[1]
            except:
                pass

            try:
                if "Interview" in line[2]:
                    data_collected["interview_difficulty"] = line[2]
            except:
                pass

        # Interview Application
        try:
            application = review.select("p.applicationDetails.continueReading")[0]
        except:
            pass
        data_collected["application"] = application.text

        # Interview Details
        try:
            interview = review.select("p.interviewDetails.continueReading")[0]
        except:
            pass
        data_collected["interview"] = interview.text

        # Interview Questions
        try:
            questions = review.select(".interviewQuestion.noPadVert.truncateThis.wrapToggleStr")[0]
        except:
            pass
        data_collected["interview_questions"] = questions.text

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
            # print(disabled)
            next_page = None
    return next_page


