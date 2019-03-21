import requests
import xml.etree.ElementTree as ET


sitemaps = []
urls = []
sites = ["evem.gov.si", "e-uprava.gov.si", "podatki.gov.si", "e-prostor.gov.si"]


def find_sitemaps(robots_url):
	r = requests.get(robots_url)
	if r.status_code == 200:
		for line in r.text.splitlines():
			line = line.strip().split(':', 1)
			if line[0].lower() == "sitemap":
				sitemaps.append(line[1].strip())

def parse_sitemap(sitemap):
	root = ET.fromstring(sitemap)
	for url in root:
		for prop in url:
			if prop.tag.endswith("loc"):
				urls.append(prop.text)

# get sitemaps
for s in sites:
	find_sitemaps("http://" + s + "/robots.txt")

# get urls from sitemaps
for sm in sitemaps:
	r = requests.get(sm)
	if r.status_code == 200:
		parse_sitemap(r.text)

# print found urls
print(urls)