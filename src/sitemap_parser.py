import requests
import xml.etree.ElementTree as ET


class SitemapParser:
	def __init__(self):
		self._sitemaps = []
		self.urls = []

	def _parse_sitemap(self, sitemap):
		try:
			root = ET.fromstring(sitemap)
			for url in root:
				for prop in url:
					if prop.tag.endswith("loc"):
						self.urls.append(prop.text.strip())
		except Exception:
			pass

	def find_sitemaps(self, base_url):
		self._sitemaps[:] = [] # clear previous entries

		root_sitemap_url = base_url + "/sitemap.xml"
		robots_url = base_url + "/robots.txt"

		# check if sitemap.xml exits on root
		r = requests.get(root_sitemap_url)
		if r.status_code == 200:
			self._sitemaps.append(root_sitemap_url)

		# check if sitemaps exist in robots.txt
		r = requests.get(robots_url)
		if r.status_code == 200:
			for line in r.text.splitlines():
				line = line.strip().split(':', 1)
				# skip gzipped sitemaps
				if line[0].lower() == "sitemap" and not \
					line[1].strip().endswith(".gz"):
					self._sitemaps.append(line[1].strip())

	def parse_sitemaps(self):
		for sm in self._sitemaps:
			r = requests.get(sm)
			if r.status_code == 200:
				self._parse_sitemap(r.text)

	def urls_to_string(self):
		return ' '.join(self.urls)
