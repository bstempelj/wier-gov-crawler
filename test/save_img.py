import requests
from os.path import splitext, basename

from PIL import Image
from io import BytesIO

url = "https://fri.uni-lj.si/sites/all/themes/fri_theme/images/fri_logo.png"

filename, ext = splitext(url)
filename = basename(filename)
r = requests.get(url)
i = Image.open(BytesIO(r.content))
i.save("images/%s%s" % (filename, ext))