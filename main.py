import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from collections import deque
import hashlib

options = Options()
options.headless = True
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

driver = webdriver.Chrome(executable_path=os.path.abspath('chromedriver'), options=options)
driver.get("http://fri.uni-lj.si")

frontier = deque()
history = dict()


for i in range(2):
    for n in driver.find_elements_by_class_name('news-container-title'):
        if len(n.text) > 0:
            m = hashlib.sha1()
            m.update(n.text.encode('utf-8'))
            hashText = m.hexdigest()
            if hashText not in history:
                history[hashText] = n.text
                frontier.append(n.text)

print(history)

driver.close()


