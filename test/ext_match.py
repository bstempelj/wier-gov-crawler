import re

url = "http://cs.indiana.edu/My%20File.htm"
p = re.compile("\\.\\w+$")

if p:
  print("MATCH")
else:
  print("NO MATCH")