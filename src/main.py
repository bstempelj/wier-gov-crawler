import os
import hashlib
import requests

from PIL import Image
from io import BytesIO
from os.path import splitext, basename

from enum import Enum
from collections import deque

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait


class Browser(Enum):
    FIREFOX = 1
    CHROME = 2

max_urls = 1000
site = "http://fri.uni-lj.si"
# site = "https://fov.um.si/sl"
img_folder = "images"
browser = Browser.FIREFOX

def norm_url(url):
    q = url.find("?")
    if q != -1:
        return url[:q]
    return url

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

    frontier = deque()
    history = dict()

    frontier.append(site)
    while len(frontier) != 0 and max_urls > 0:
        driver.get(frontier.pop())

        # get all urls from a site
        for n in driver.find_elements_by_xpath("//a[@href]"):
            link = n.get_attribute("href")
            if len(link) > 0:
                m = hashlib.sha1()
                m.update(link.encode('utf-8'))
                hashText = m.hexdigest()
                if hashText not in history:
                    history[hashText] = link
                    frontier.append(link)
            max_urls -= 1

        # get all images from a site
        for n in driver.find_elements_by_tag_name("img"):
            img_url = n.get_attribute("src")
            save_img(img_url)


    driver.close()

    for url in history.values():
        print(url)
