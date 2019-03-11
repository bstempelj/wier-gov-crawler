from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

if __name__ == "__main__":
  options = Options()
  options.add_argument('-headless')
  driver = Firefox(executable_path='geckodriver', options=options)
  wait = WebDriverWait(driver, timeout=10)
  driver.get('http://evem.gov.si')
  # driver.execute_script('Location()')
  print(driver.page_source)
  driver.quit()