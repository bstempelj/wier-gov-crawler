def save_img(url):
	url = norm_url(url)
	filename, ext = splitext(url)
	if ext in [".png", ".jpg", ".jpeg", ".gif"]:
		filename = basename(filename)
		print("Downloading: %s" % filename)
		r = requests.get(url)
		i = Image.open(BytesIO(r.content))
		i.save("images/%s%s" % (filename, ext))

def norm_url(url):
	q = url.find("?")
	if q != -1:
		return url[:q]
	return url

if __name__ == "__main__":
	for n in driver.find_elements_by_tag_name("//img[@src]"):
		img_url = n.get_attribute("src")
		save_img(img_url)