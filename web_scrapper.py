import requests
from bs4 import BeautifulSoup
import json


def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


listing_html = requests.get(
    "https://www.linkedin.com/jobs/software-engineer-intern-jobs-united-states/")

doc = BeautifulSoup(listing_html.text, "html.parser")


jobs_ul = doc.find("ul", {"class": "jobs-search__results-list"})

data_dump = {}
for li in jobs_ul.find_all("li"):
    try:
        posting_url = li.div.a['href']
        posting_url = posting_url.split("?", 1)[0]
        temp_dict = {}
        posting_html = requests.get(
            posting_url)
        listing = BeautifulSoup(posting_html.text, "html.parser")
        job_title = listing.find(
            "h1", {"class": "top-card-layout__title topcard__title"}).string
        temp_dict['job_title'] = job_title.strip()
        company_name = listing.find(
            "a", {"class": "topcard__org-name-link"}).string
        temp_dict['company_name'] = company_name.strip()
        location = listing.find(
            "span", {"class": "topcard__flavor topcard__flavor--bullet"}).string
        temp_dict['location'] = location.strip()
        description = listing.find(
            "div", {"class": "description__text"}).find("div", {"class": "show-more-less-html__markup"})
        temp_dict['description'] = remove_html_tags(str(description)).strip()
        data_dump[posting_url] = temp_dict
    except Exception:
        with open('error.txt', 'w') as file:
            file.write(posting_url)

with open('result.json', 'w') as file:
    json.dump(data_dump, file, indent=4)
