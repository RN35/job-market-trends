""" This scripts scrapes LinkedIn job listings and saves details locally in json format """
import logging
import re
import json
from datetime import datetime
import traceback
import sys
import requests
from bs4 import BeautifulSoup
from slugify import slugify


def remove_html_tags(text):
    """Removes html tags from a string"""
    return re.sub(re.compile("<.*?>"), "", text)


def get_html_for_web_page(url):
    """Makes a get request to retrieve html"""
    html = requests.get(url)
    return html.text


def save_dict_to_file(input_dict, file):
    """Writes dictionnary to a file"""
    with open(file, "w") as result_file:
        json.dump(input_dict, result_file, indent=4)


def fetch_listing(posting_url):
    """Makes a get request to retrieve html"""
    listing_info = {}
    # get web page of specific listing
    listing_doc = BeautifulSoup(get_html_for_web_page(posting_url), "html.parser")

    # retrieve title
    job_title = listing_doc.find(
        "h1", {"class": "top-card-layout__title topcard__title"}
    ).string
    listing_info["job_title"] = job_title.strip()
    company_name = listing_doc.find("a", {"class": "topcard__org-name-link"}).string

    # retrieve company
    listing_info["company_name"] = company_name.strip()
    location = listing_doc.find(
        "span", {"class": "topcard__flavor topcard__flavor--bullet"}
    ).string

    # retrieve location
    listing_info["location"] = location.strip()
    description = listing_doc.find("div", {"class": "description__text"}).find(
        "div", {"class": "show-more-less-html__markup"}
    )

    # retrieve description
    listing_info["description"] = remove_html_tags(str(description)).strip()
    return listing_info


def get_job_listings(role, location):
    """Parses through LinkedIn jobs page to get listings"""
    url = f"https://www.linkedin.com/jobs/{ slugify(role)}-jobs-{slugify(location)}/"
    doc = BeautifulSoup(get_html_for_web_page(url), "html.parser")
    logging.info(
        "Fetched html for role %s location %s using url %s", role, location, url
    )
    jobs_ul = doc.find("ul", {"class": "jobs-search__results-list"})
    all_listing = {}

    for listing in jobs_ul.find_all("li"):
        # fetch job listing and parse it
        try:
            # retrieve posting url from <li> tag
            posting_url = listing.div.a["href"]
            posting_url = posting_url.split("?", 1)[0]

            listing_info = fetch_listing(posting_url)

            all_listing[posting_url] = listing_info
            logging.info(
                "Retrieving listing for job posting %s successful", posting_url
            )
        except Exception:
            logging.error("Retrieving listing for job posting %s failed", posting_url)
            full_traceback = str(traceback.format_exc())
            logging.error(full_traceback)

    return all_listing


def main():
    """This is the main function"""
    try:
        start_timestamp = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        log_file = f"{ start_timestamp }.log"
        logging.basicConfig(
            filename=log_file,
            filemode="a",
            format="*%(asctime)s APP_%(levelname)s [%(module)s>%(funcName)s]: %(message)s",
            level="INFO",
            datefmt="%y/%m/%d %H:%M:%S",
        )

        listings_dict = get_job_listings("Software Engineer Intern", "United States")
        save_dict_to_file(listings_dict, "result.json")
        logging.info("Saved results in file result.json")
    except Exception:
        full_traceback = str(traceback.format_exc())
        logging.error(full_traceback)
        sys.exit(1)


if __name__ == "__main__":
    main()
