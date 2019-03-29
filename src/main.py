import os
import requests
from database import Database

from sitemap_parser import SitemapParser
from frontier import Frontier

from PIL import Image
from io import BytesIO
from os.path import splitext, basename

from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

from enum import Enum

from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Browser(Enum):
    FIREFOX = 1
    CHROME = 2


seed = ["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"]


# site = "https://podatki.gov.si"
# site = "https://fov.um.si/sl"


img_folder = "images"
browser = Browser.CHROME


def norm_url(url):
    q = url.find("?")
    if q != -1:
        return url[:q]
    return url


def get_base_url(url):
    split_url = urlsplit(url)
    return "://".join([split_url.scheme, split_url.netloc])


def has_robots_file(url):
    r = requests.get(get_base_url(url) + "/robots.txt")
    return r.status_code == 200, r.text


def get_urls(driver, frontier):
    # for n in driver.find_elements_by_xpath("//*[@onclick]"):
    #     print(n)

    for n in driver.find_elements_by_xpath("//a[@href]"):
        link = n.get_attribute("href")
        if len(link) > 0 and link != "javascript:void(0)":
            frontier.add_url(link)


def save_img(url):
    url = norm_url(url)
    filename, ext = splitext(url)
    if ext in [".png", ".jpg", ".jpeg", ".gif"]:
        filename = basename(filename)
        print("Downloading: %s" % filename)
        r = requests.get(url)
        i = Image.open(BytesIO(r.content))
        i.save("images/%s%s" % (filename, ext))

def check_if_doc(url):
    url = norm_url(url)
    url, ext = splitext(url)
    if ext in [".doc", ".docx", ".pdf", ".xlsx", ".xls", ".PPT"]:




if __name__ == "__main__":

    if browser == Browser.FIREFOX:
        options = FirefoxOptions()
        options.headless = True
        driver = Firefox(executable_path="geckodriver", options=options)
    else:
        options = ChromeOptions()
        options.headless = True
        driver = Chrome(executable_path="chromedriver", options=options)

    frontier = Frontier()
    robots = []
    rp = RobotFileParser()
    sp = SitemapParser()
    db = Database()
    site_id = -1

    frontier.add_urls(seed)
    while frontier.has_urls() and not frontier.max_reached():
        # url info -
        url = frontier.get_next().replace("www.", "")
        base_url = get_base_url(url)
        robots_url = base_url + "/robots.txt"

        # Check that we are still on track
        if base_url not in seed:
            continue

        # connect to website
        print(url)
        http_head = requests.head(url)  # .page_source v bazo
        driver.get(url)

        # check for robots.txt
        robot_file = has_robots_file(url)
        if base_url not in robots and robot_file[0]:
            robots.append(base_url)

        # respect robots.txt
        if base_url in robots:
            rp.set_url(robots_url)
            rp.read()

            # parse sitemap
            sp.find_sitemaps(robots_url)
            sp.parse_sitemaps()

            # Write site to database
            db.add_site(base_url, robot_file[1], sp.get_sitemaps())
            frontier.add_urls(sp.urls)

            if rp.can_fetch("*", url):
                get_urls(driver, frontier)
        else:
            # no robots.txt => parse everything :)
            # Write site to database without
            db.add_site(base_url, None, None)
            get_urls(driver, frontier)

        date_res = None
        if 'Date' in http_head.headers:
            date_res = http_head.headers['Date']

        db.add_page(http_head.url, driver.page_source, http_head.status_code, date_res)

        # get all images from a site
        """
        for n in driver.find_elements_by_tag_name("//img[@src]"):
            img_url = n.get_attribute("src")
            save_img(img_url)
        """

    driver.close()

    # print history
    for url in frontier._history.values():
        print(url)
