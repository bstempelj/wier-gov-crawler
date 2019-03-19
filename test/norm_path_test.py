from os.path import normpath, normcase

url1 = "http://cs.indiana.edu/a/./../b/"
url2 = "http://cs.indiana.edu/b/"
url3 = "https://fov.um.si/sites/default/files/styles/current_80x80/public/upload/current/images/pds-icon.png?itok=duk4wIIG"

double_idx = url3.find("//")
print(normpath(url3[double_idx+2:]).replace("\\", "/"))