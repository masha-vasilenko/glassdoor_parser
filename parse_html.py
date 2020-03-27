from bs4 import BeautifulSoup

with open('result.html') as f:
    html = f.read()
# Get BeautifulSoup

soup = BeautifulSoup(html, features="html.parser")

# Get roles to which reviewers applied
for review in soup.select("li.empReview.cf"):
    header = review.select("h2.summary.strong.noMargTop.tightTop.margBotXs")[0]
    print(header.text)

final_results = []
for review in soup.select("li.empReview.cf"):
    data_collected = {"role": [], "offer": None, "impression": None, "interview_difficulty": None}
    # Get role
    role = review.select("h2.summary.strong.noMargTop.tightTop.margBotXs")[0]
    data_collected["role"] = role.text
    final_results.append(data_collected)

    # Impressions
    outcomes = review.select(".interviewOutcomes")
    for out in outcomes:
        middle_panel = out.select(".middle")
        line = []
        for elem in middle_panel:
            if list((elem.select("span", class_="middle"))) != []:
                el = elem.select("span", class_="middle")[0].text
                print(el)
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

print(final_results)
