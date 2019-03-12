import re

p = re.compile("\\s")
url = "%20".join(p.split("http://cs.indiana.edu/My Secret File.htm"))
print(url)