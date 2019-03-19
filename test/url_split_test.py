from urllib.parse import urlsplit

url = "https://preshing.com/20171218/how-to-write-your-own-cpp-game-engine/"
url2 = "https://wiki.libsdl.org/APIByCategory"

def baseurl(url):
	split_url = urlsplit(url)
	return "://".join([split_url.scheme, split_url.netloc])

print(baseurl(url2))