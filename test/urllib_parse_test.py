from urllib.parse import urlparse

test_cases = [
	["http://cs.indiana.edu:80/", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu:80", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu/People", "http://cs.indiana.edu/People/"],
	["http://cs.indiana.edu/faq.html#3", "http://cs.indiana.edu/faq.html"],
	["http://cs.indiana.edu/a/./../b/", "http://cs.indiana.edu/b/"],
	["http://cs.indiana.edu/index.html", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu/%7Efil/", "http://cs.indiana.edu/~fil/"],
	["http://cs.indiana.edu/My File.htm", "http://cs.indiana.edu/My%20File.htm"],
	["http://CS.INDIANA.EDU/People", "http://cs.indiana.edu/People/"],
]

for t in test_cases:
	print(urlparse(t[0]))