from urllib.parse import urlparse, quote, unquote
from os.path import splitext, basename, normpath

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
	url = urlparse(url)

	# lowercase network part
	url = url._replace(netloc=url.netloc.lower())

	# unquote and quote path
	url = url._replace(path=unquote(url.path))
	url = url._replace(path=quote(url.path))

	# normalize path
	if url.path != "":
		url = url._replace(path=normpath(url.path).replace("\\", "/"))

	# remove port from url
	port = url.netloc.find(":")
	if port != -1:
		no_port = url.netloc[:port]
		url = url._replace(netloc=no_port)

	# path/file and file extension
	path, ext = splitext(url.path)

	# add trailing slash to netloc
	if path == "":
		url = url._replace(netloc=url.netloc + "/")
	# add trailing slash to path
	elif ext == "" and not path.endswith("/"):
		url = url._replace(path=url.path + "/")
	# remove index.html
	elif ext == ".html" and path.endswith("index"):
		url = url._replace(path="/")

	return "{}://{}{}".format(url.scheme, url.netloc, url.path)

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
