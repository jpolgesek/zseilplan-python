#coding: UTF-8
import requests
import json
from pywebpush import webpush

PRIVATE_KEY = "***REMOVED***"

r = requests.get("https://testplan.polgesek.pl/subscriptions.json")
subs = r.json()

def send_push(s, data):
	aud = s["endpoint"].split("https://")[1].split("/")[0]
	aud = "https://"+aud

	return webpush(s,
		data = data,
		vapid_private_key = PRIVATE_KEY,
		vapid_claims = {"sub":"mailto:zseilplan@polgesek.pl", "aud": aud}
	)

data = {
	"title": "Super Clever Plan - Nowy Plan",
	"body": "Już jest! Nowy, lepszy plan. Nie było już przecież zmiany od {} dni".format("__TODO__"),
	"icon": 'img/launcher-icon-4x.png'
}

#data = {}

#send_push(sub, json.dumps(data))

def send_to(recipient, title="Super Clever Plan", message="", url="https://dev.polgesek.pl/zseilplan/", icon="assets/img/launcher-icon-4x.png"):
	notification_data = json.dumps({
		"title": title, 
		"body": message, 
		"icon": icon
	})

	aud = "https://" + (recipient["endpoint"].split("https://")[1].split("/")[0])
	try:
		return webpush(recipient,
			data = notification_data,
			vapid_private_key = PRIVATE_KEY,
			vapid_claims = {"sub":"mailto:zseilplan@polgesek.pl", "aud": aud}
		)
	except:
		pass


def send_to_all(title="Super Clever Plan", message="", url="https://dev.polgesek.pl/zseilplan/", icon="assets/img/launcher-icon-4x.png"):
	for k in subs:
		send_to(subs[k], title=title, message=message, url=url, icon=icon)
	return True


if __name__ == "__main__":
	print("This should not be called directly")
	# send_to_all(title="Super promocja!", message="Teraz w pizzy hut duża pizza tylko 29,99. A przy okazji testuję cross-origin i nowy silnik powiadomień")
	send_to_all(title="Super Clever Plan - Nowy Plan", message="Już jest! Nowy, lepszy plan. Nie było już przecież zmiany od {} dni".format("__TODO__"))
