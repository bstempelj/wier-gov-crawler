from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

def contains(s, attrs):
	res = [s.find(a) != -1 for a in attrs]
	return True in res

options = Options()
options.headless = True
driver = Firefox(executable_path="geckodriver", options=options)

starting_url = "https://www.plus2net.com/html_tutorial/button-linking.php"

driver.get(starting_url)

loc_attrs = [
	"location.href",
	# "location.assign",
	"parent.location",
	"parent.open",
	"window.open"]

links = []
for n in driver.find_elements_by_xpath("//*[@onclick]"):
	onclick = n.get_attribute("onclick")
	link = ""

	if contains(onclick, ["parent.open", "window.open"]):
		link = onclick.split("(")[1]
		link = link.split(",")
		link = link[0] if len(link) != 1 else link[0][:-1]
	elif contains(onclick, ["location.href", "parent.location"]):
		link = onclick.split("=")[1].strip()

	print(link)