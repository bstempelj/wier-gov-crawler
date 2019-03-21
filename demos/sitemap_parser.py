import requests
import xml.etree.ElementTree as ET


class SitemapParser:
	def __init__(self):
		self._sitemaps = []
		self.urls = []

	def _parse_sitemap(self, sitemap):
		root = ET.fromstring(sitemap)
		for url in root:
			for prop in url:
				if prop.tag.endswith("loc"):
					self.urls.append(prop.text)

	def find_sitemaps(self, robots_url):
		r = requests.get(robots_url)
		if r.status_code == 200:
			for line in r.text.splitlines():
				line = line.strip().split(':', 1)
				if line[0].lower() == "sitemap":
					self._sitemaps.append(line[1].strip())

	def parse_sitemaps(self):
		for sm in self._sitemaps:
			r = requests.get(sm)
			if r.status_code == 200:
				self._parse_sitemap(r.text)


if __name__ == "__main__":
	sites = ["evem.gov.si", "e-uprava.gov.si", "podatki.gov.si", "e-prostor.gov.si"]
	
	sp = SitemapParser()

	# get sitemaps
	for s in sites:
		sp.find_sitemaps("http://" + s + "/robots.txt")

	sp.parse_sitemaps()
	print(sp.urls)