import requests
from urllib.robotparser import RobotFileParser

url = "http://fri.uni-lj.si/"
url2 = "https://github.com/robots.txt"

def has_robots_file(url):
	r = requests.get(url)
	return r.status_code == 200

def read_robots_file(url):
	r = requests.get(url)
	return r.text

def allowed_url(url):
	rp = RobotFileParser()
	return rp.can_fetch("*", url)

rp = RobotFileParser()
rp.set_url(url2)
rp.read()
rrate = rp.request_rate("*")
print(rrate)

# print("FRI: %s" % read_robots_file(url))
# print("Github: %s" % read_robots_file(url2))

# print(allowed_url("https://github.com/bstempelj"))