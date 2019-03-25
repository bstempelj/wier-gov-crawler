import os
import requests

from sitemap_parser import SitemapParser
from frontier import Frontier
from database import connect

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


class Browser(Enum):
    FIREFOX = 1
    CHROME = 2


seed = ["evem.gov.si", "e-uprava.gov.si", "podatki.gov.si", "e-prostor.gov.si"]

# site = "http://fri.uni-lj.si"
# site = "https://fov.um.si/sl"
site = "http://www.e-prostor.gov.si"
#site = "http://e-uprava.gov.si"

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
    return r.status_code == 200

def get_urls(driver, frontier):
    for n in driver.find_elements_by_xpath("//a[@href]"):
        link = n.get_attribute("href")
        if len(link) > 0:
            frontier.add_url(link)

def save_img(url):
    url = norm_url(url)
    filename, ext = splitext(url)
    if ext in [".png", ".jpg", ".jpeg"]:
        filename = basename(filename)
        print("Downloading: %s" % filename)
        r = requests.get(url)
        i = Image.open(BytesIO(r.content))
        i.save("images/%s%s" % (filename, ext))


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

    #connect to database
    connect()

    frontier.add_url(site)
    while frontier.has_urls() and not frontier.max_reached():
        # url info
        url = frontier.get_next()
        print(url)
        # print(url)
        base_url = get_base_url(url)
        robots_url = base_url + "/robots.txt"

        # connect to website
        driver.get(url) # .page_source v bazo

        # check for robots.txt
        if base_url not in robots and has_robots_file(url):
            robots.append(base_url)

        # respect robots.txt
        if base_url in robots:
            rp.set_url(robots_url)
            rp.read()

            # parse sitemap
            sp.find_sitemaps(robots_url)
            sp.parse_sitemaps()
            frontier.add_urls(sp.urls)

            if rp.can_fetch("*", url):
                get_urls(driver, frontier)
        else:
            # no robots.txt => parse everything :)
            get_urls(driver, frontier)

        # get all images from a site
        # for n in driver.find_elements_by_tag_name("//img[@src]"):
        #     img_url = n.get_attribute("src")
        #     save_img(img_url)

    driver.close()

    # print history
    for url in frontier._history.values():
        print(url)
