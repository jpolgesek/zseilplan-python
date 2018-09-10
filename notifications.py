#coding: UTF-8
import requests
import json
from pywebpush import webpush
import os
import config
import datetime
import ftplib
from collections import OrderedDict

target = {}

ARCHIVE_DIR = "archive"

PRIVATE_KEY = "***REMOVED***"

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


with open(os.path.join(ARCHIVE_DIR, "internal_index.json"), "r") as f:
	hashes = json.load(f)

hashes_2 = {}
for k in hashes:
	hashes_2[hashes[k]] = k
hashes_2 = sorted(hashes_2)

date_new = hashes_2[-1]
date_old = hashes_2[-2]

date_new = datetime.datetime.strptime(date_new, "%d.%m.%Y %H:%M:%S")
date_old = datetime.datetime.strptime(date_old, "%d.%m.%Y %H:%M:%S")

difference = date_new - date_old
difference_hour = difference.seconds//3600
difference_minute = (difference.seconds//60)%60

if difference.days == 0:
	if difference_hour == 0:
		difference_string = "{} minut".format(difference_minute)
	else:
		difference_string = "{} godzin".format(difference_hour)
elif difference.days == 1:
	difference_string = "{} dnia".format(difference.days)
else:
	difference_string = "{} dni".format(difference.days)


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
	message = "Już jest! Nowy, lepszy plan. Nie było już przecież zmiany od {}".format(difference_string)

	for k in subs:
		send_to(subs[k], title=title, message=message, url=url, icon=icon)
	return True


if __name__ == "__main__":
	print("This should not be called directly")
	# send_to_all(title="Super promocja!", message="Teraz w pizzy hut duża pizza tylko 29,99. A przy okazji testuję cross-origin i nowy silnik powiadomień")
	send_to_all(title="Super Clever Plan - Nowy Plan")



def start():
	global subs

	print("Get subscriptions list")

	ftp = ftplib.FTP(target['hostname'])
	ftp.login(user = target['ftp_user'], passwd = target['ftp_pass'])
	ftp.cwd(target['ftp_rootdir_app'])
	
	with open(".htsubscriptions.json", 'wb') as f:
		ftp.retrbinary('RETR .htsubscriptions.json', f.write)
		
	with open(".htsubscriptions.json", 'r', encoding="UTF-8") as f:
		subs = json.load(f)
	
	print("Ilość subskrybcji: {}".format(len(subs)))

	send_to_all()
	
	print("Update subscriptions list [todo]")
	'''
	ftp = ftplib.FTP(target['hostname'])
	ftp.login(user = target['ftp_user'], passwd = target['ftp_pass'])
	ftp.cwd(target['ftp_rootdir_app'])
	ftp.storbinary('STOR .htsubscriptions.json', open(".htsubscriptions.json", 'rb'))
	'''
