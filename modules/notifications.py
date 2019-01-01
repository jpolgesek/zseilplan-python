#coding: UTF-8
import os
import json
import time
import config
import datetime
import requests
from pywebpush import webpush
from collections import OrderedDict


class Notification:
	private_key = "***REMOVED***"
	subscriptions_filename = ".htsubscriptions.json"

	def __init__(self, cfg, forced = False):
		self.archive_dir = os.path.join("", "archive")
		self.cfg = cfg
		
		diff = self.get_diff_string()

		print("Stan diff'a: {}".format(diff))

		if diff != False or forced:
			if forced:
				print("WYSŁANIE POWIADOMIENIA WYMUSZONE")
				message = "Już jest! Nowy, lepszy plan."
			else:
				message = "Już jest! Nowy, lepszy plan. Nie było przecież zmiany aż od {}".format(diff)
			
			url = "https://{}{}".format(cfg.target["hostname"], cfg.target["http_rootdir_app"])

			self.subscriptions = self.get_subscriptions()
			self.verified_subscriptions = {}
			self.send_to_discord(message=message, url=url)
			self.send_to_all(message=message, url=url)

			if len(self.verified_subscriptions) > 0:
				self.set_subscriptions(self.verified_subscriptions)
		else:
			print("Nie ma potrzeby wysyłania powiadomienia")
			print("Użyj parametru --force-notification aby to wymusić")
			
		return

	def send_to_discord(self, message, url):
		url = "https://discordapp.com/api/webhooks/***REMOVED***/***REMOVED***"
		return requests.post(url, data={
  			"content": message
		})

	def get_subscriptions(self):
		self.cfg.uploader.chdir(self.cfg.target["rootdir_app"])
		data = self.cfg.uploader.fetch_file(self.subscriptions_filename)
		data = data.decode("UTF-8")
		data = json.loads(data)
		print("Znaleziono {} subskrybcji".format(len(data)))
		return data
	
	def set_subscriptions(self, data):
		data = json.dumps(data)
		with open(self.subscriptions_filename, "w", encoding="UTF-8") as f:
			f.write(data)
		self.cfg.uploader.chdir(self.cfg.target["rootdir_app"])
		self.cfg.uploader.upload_file(self.subscriptions_filename, self.subscriptions_filename)
		os.unlink(self.subscriptions_filename)
		return True

	def send_single(self, recipient, title="Super Clever Plan", message="", url="https://dev.polgesek.pl/zseilplan/", icon="assets/img/launcher-icon-4x.png"):
		notification_data = json.dumps({
			"title": title, 
			"body": message, 
			"icon": icon,
			"clickUrl": url
		})

		aud = "https://" + (recipient["endpoint"].split("https://")[1].split("/")[0])

		try:
			return webpush(recipient,
				data = notification_data,
				vapid_private_key = self.private_key,
				vapid_claims = {"sub":"mailto:zseilplan@polgesek.pl", "aud": aud}
			)
		except:
			return False
		
	def send_to_all(self, title="Super Clever Plan", message="", url="https://dev.polgesek.pl/zseilplan/", icon="assets/img/launcher-icon-4x.png"):
		for sub in self.subscriptions:
			resp = self.send_single(self.subscriptions[sub], title=title, message=message, url=url, icon=icon)
			if resp != False:
				self.verified_subscriptions[sub] = self.subscriptions[sub]

	def get_diff_string(self):
		with open(os.path.join(self.archive_dir, "internal_index.json"), "r") as f:
			hashes = json.load(f)
		
		if not os.path.exists(os.path.join(self.archive_dir, "notifications_index.json")):
			with open(os.path.join(self.archive_dir, "notifications_index.json"), "w", encoding="UTF-8") as f:
				f.write(json.dumps({"sentFor": []}))
		
		with open(os.path.join(self.archive_dir, "notifications_index.json"), "r") as f:
			sentFor = json.load(f)
		
		if len(hashes) < 2:
			return False

		hashes_2 = {}
		for k in hashes:
			# k => hash
			#date = hashes[k]
			date = int(time.mktime(datetime.datetime.strptime(hashes[k], "%d.%m.%Y %H:%M:%S").timetuple()))
			hashes_2[date] = {
				"k": k,
				"o_date": hashes[k]
			}
		hashes_by_date = hashes_2
		hashes_2 = sorted(hashes_2)

		date_new = hashes_by_date[hashes_2[-1]]["o_date"]
		date_old = hashes_by_date[hashes_2[-2]]["o_date"]

		date_new = datetime.datetime.strptime(date_new, "%d.%m.%Y %H:%M:%S")
		date_old = datetime.datetime.strptime(date_old, "%d.%m.%Y %H:%M:%S")

		print("Diff new: {}".format(str(date_new)))
		print("Diff old: {}".format(str(date_old)))

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
		
		if hashes_by_date[hashes_2[-1]]["k"] not in sentFor["sentFor"]:
			print("Sending first time for hash: {}".format(hashes_by_date[hashes_2[-1]]["k"]))
			sentFor["sentFor"].append(hashes_by_date[hashes_2[-1]]["k"])
			with open(os.path.join(self.archive_dir, "notifications_index.json"), "w", encoding="UTF-8") as f:
				f.write(json.dumps(sentFor))
			return difference_string
		else:
			print("Already sent notification for hash: {}".format(hashes_by_date[hashes_2[-1]]["k"]))
			return False



if __name__ == "__main__":
	print("This program should not be called directly")
	exit()
	# send_to_all(title="Super promocja!", message="Teraz w pizzy hut duża pizza tylko 29,99. A przy okazji testuję cross-origin i nowy silnik powiadomień")