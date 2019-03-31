import os
import ssl
import requests
from database import Database

from sitemap_parser import SitemapParser
from frontier import Frontier
import sys
import time

from PIL import Image
from io import BytesIO
from os.path import splitext, basename
import threading as th

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

# disable SSL (don't try this at home kids)
ssl._create_default_https_context = ssl._create_unverified_context

class Browser(Enum):
    FIREFOX = 1
    CHROME = 2


use_database = False
seed = ["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"]
browser = Browser.FIREFOX


def get_base_url(url):
    split_url = urlsplit(url)
    return "://".join([split_url.scheme, split_url.netloc])


def has_robots_file(url):
    r = requests.get(get_base_url(url) + "/robots.txt")
    return r.status_code == 200, r.text


def get_urls(driver, frontier):
    global seed

    for n in driver.find_elements_by_xpath("//a[@href]"):
        link = n.get_attribute("href")
        if len(link) > 0 and \
            link != "javascript:void(0)" and \
            get_base_url(link) in seed:
                frontier.add_url(link)

    # Parsing images
    for n in driver.find_elements_by_xpath("//img[@src]"):
        url = n.get_attribute("src")
        filename, ext = splitext(url)
        if ext in [".png", ".jpg", ".jpeg", ".gif"] and \
            get_base_url(url) in seed:
                # print(url)
                frontier.add_url(url)


def crawler(th_num, frontier, db, rp, sp, robots):
    # Driver for selenium
    if browser == Browser.FIREFOX:
        options = FirefoxOptions()
        options.headless = True
        driver = Firefox(executable_path="geckodriver", options=options)
    else:
        options = ChromeOptions()
        options.headless = True
        driver = Chrome(executable_path="chromedriver", options=options)

    """
    print('Start thread ' + th_num)
    if th_num == '1':
        time.sleep(30)
    """

    while frontier.has_urls() and not frontier.max_reached():
        # url info -
        url = frontier.get_next()
        base_url = get_base_url(url)
        robots_url = base_url + "/robots.txt"

        # Check that we are still on track
        if base_url not in seed:
            continue

        # connect to website
        print('Thread: ' + th_num + ' - ' + url)
        http_head = requests.head(url)  # .page_source v bazo

        # Skip links which give 404 not found (links still exists but file doesnt anymore)
        if http_head.status_code == 404:
            continue

        try:
            driver.get(url)
        except Exception as e:
            options = ChromeOptions()
            options.headless = True
            driver = Chrome(executable_path="chromedriver", options=options)
            continue

        is_html = True
        if 'Content-Type' in http_head.headers:
            con_type = http_head.headers['Content-Type']
            is_html = True if con_type.find('html', 0) > -1 else False


        # check for robots.txt
        robot_file = has_robots_file(url)
        if base_url not in robots and robot_file[0]:
            robots.append(base_url)

        # respect robots.txt
        if base_url in robots and is_html:
            rp.set_url(robots_url)
            rp.read()

            # parse sitemap
            sp.find_sitemaps(robots_url)
            sp.parse_sitemaps()

            # Write site to database
            db.add_site(base_url, robot_file[1], sp.urls_to_string())
            frontier.add_urls(sp.urls)

            if rp.can_fetch("*", url):
                get_urls(driver, frontier)
        elif is_html:
            # no robots.txt => parse everything :)
            # Write site to database without
            db.add_site(base_url, None, None)
            get_urls(driver, frontier)

        date_res = None
        if 'Date' in http_head.headers:
            date_res = http_head.headers['Date']

        db.add_page(http_head.url, driver.page_source, http_head.status_code, date_res)

        if not frontier.has_urls():
            print(th_num + " sleep")
            time.sleep(10)

    driver.close()


if __name__ == "__main__":
    frontier = Frontier()
    robots = []
    rp = RobotFileParser()
    sp = SitemapParser()
    db = Database(use_database)

    frontier.add_urls(seed)

    # Read thread num argument
    thread_num = 1
    if len(sys.argv) > 1:
        thread_num = int(sys.argv[1])

    th_list = list()
    for i in range(thread_num):
        th_list.append(th.Thread(target=crawler, args=(str(i), frontier, db, rp, sp, robots)))

    for i in range(thread_num):
        th_list[i].start()

    for i in range(thread_num):
        th_list[i].join()

    # get all images from a site
    """
    for n in driver.find_elements_by_tag_name("//img[@src]"):
        img_url = n.get_attribute("src")
        save_img(img_url)
    """

    # print history
    for url in frontier._history.values():
        print(url)

