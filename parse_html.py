from bs4 import BeautifulSoup

with open('result.html') as f:
    html = f.read()
# Get BeautifulSoup

soup = BeautifulSoup(html, features="html.parser")

# Get roles to which reviewers applied
for review in soup.select("li.empReview.cf"):
    header = review.select("h2.summary.strong.noMargTop.tightTop.margBotXs")[0]
    print(header.text)

