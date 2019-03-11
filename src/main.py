import os
import hashlib

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

site = "http://fri.uni-lj.si"
browser = Browser.FIREFOX

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

    driver.get(site)

    for n in driver.find_elements_by_xpath("//a[@href]"):
        link = n.get_attribute("href")
        if len(link) > 0:
            if link[-1:] == "/":
                print(link)
            else:
                continue
            m = hashlib.sha1()
            m.update(link.encode('utf-8'))
            hashText = m.hexdigest()
            if hashText not in history:
                history[hashText] = link
                frontier.append(link)

    print(history)

    driver.close()
