import requests

seed = ["http://evem.gov.si", "http://e-uprava.gov.si", "http://podatki.gov.si", "http://e-prostor.gov.si"]

for s in seed:
	r = requests.get(s + "/robots.txt")
	if r.status_code == 200:
		print(s)
		print("---")
		print(r.text)
