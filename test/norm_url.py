import re

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


def norm_url(url):
	# find port
	try:
		double_idx = url.index("//")
		port_idx = url.index(":", double_idx)

		url = url[:port_idx]
	except:
		pass

	# remove trailing hash
	try:
		hash_idx = url.index("#")
		url = url[:hash_idx]
	except:
		pass

	# remove index.html
	try:
		root_idx = url.index("index.html")
		url = url[:root_idx]
	except:
		pass

	# lowercase untils first slash
	double_idx = url.find("//")
	slash_idx = url.find("/", double_idx+2)
	url = url[:slash_idx].lower() + url[slash_idx:]

	# convert spaces to %20
	spc_p = re.compile("\\s")
	url = "%20".join(spc_p.split(url))

	# find extension
	ext_p = re.compile("\\/[A-Za-z%20]+\\.\\w+$")
	found_ext = ext_p.search(url)

	return url + ("/" if found_ext is None else "")

if __name__ == "__main__":
	total = len(test_cases)
	passed = 0
	for i, test in enumerate(test_cases):
		print("TEST {}: ".format(i+1), end="")
		result = norm_url(test[0]) == test[1]

		if result:
			print("PASSED")
			passed += 1
		else:
			print("FAILED!!")

	print("\nRATIO: {}/{}".format(passed, total))
