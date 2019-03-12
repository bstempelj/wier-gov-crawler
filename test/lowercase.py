url = "http://CS.INDIANA.EDU/People"

double_idx = url.find("//")
slash_idx = url.find("/", double_idx+2)

url = url[:slash_idx].lower() + url[slash_idx:]
print(url)