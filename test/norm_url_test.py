test_cases = [
	["http://cs.indiana.edu:80/", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu:80", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu/People", "http://cs.indiana.edu/People/"],
	["http://cs.indiana.edu/faq.html#3", "http://cs.indiana.edu/faq.html"],
	["http://cs.indiana.edu/a/./../b/", "http://cs.indiana.edu/b/"],
	["http://cs.indiana.edu/index.html", "http://cs.indiana.edu/"],
	["http://cs.indiana.edu/%7Efil/", "http://cs.indiana.edu/~fil/"],
	["http://cs.indiana.edu/My File.htm", "http://cs.indiana.edu/My % 20File.htm"],
	["http://CS.INDIANA.EDU/People", "http://cs.inidiana.edu/People"],
]


def norm_url(url):
	# find port
	try:
		double_idx = url.index("//")
		port_idx = url.index(":", double_idx)

		url = url[:port_idx] + "/"
	except:
		pass

	return url

if __name__ == "__main__":
	for i, test in enumerate(test_cases):
		print("TEST {}: ".format(i+1), end="")
		print(norm_url(test[0]) == test[1])
