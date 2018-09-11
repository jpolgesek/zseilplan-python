#coding: utf-8
import sys
import time

#sprawdz czy to python 3
if sys.version_info < (3, 0):
	print("Program wymaga pythona 3.x. Sorry :/")
	sys.exit(1)

if sys.version_info < (3, 7):
	print("Program preferuje pythona 3.7, ale pozwoli się uruchomić na pythonie 3.x")
	print("UWAGA! utils.hash może nie działać poprawnie.")

print("[*] Ładowanie programu")
import timetable_parser
import overrides_parser
import collections
import utils
from datetime import datetime
import json
import os
import ftplib
import argparse
import indexer 

try:
	import notifications
	print("notification import ok!")
except:
	print("notification import fail!")

timetable = None

print("[*] Wczytywanie konfiguracji")
import config

parser = argparse.ArgumentParser()
parser.add_argument("target")
parser.add_argument("--notificationtest", help="Send test notification to all", action="store_true")
args = parser.parse_args()

if args.target not in config.targets:
	print("[-] Niewłaściwy target: {}".format(args.target))
	print("[-] Właściwe: {}".format(', '.join(config.targets)))
	exit()

target = config.targets[args.target]

print("[*] Załadowana konfiguracja:")
print("[*] - Silnik planu lekcji: {}".format(config.timetable_engine))

if config.timetable_engine == "www":
	print("[*] - URL planu lekcji: {}".format(config.timetable_url))
	timetable = timetable_parser.www_parser(config.timetable_url)
elif config.timetable_engine == "vulcan":
	print("[*] - Vulcan login: {}".format(config.vulcan_login))

print("[*] - Silnik listy zastępstw: {}".format(config.overrides_engine))

if config.overrides_engine == "www":
	print("[*] - URL listy zastępstw: {}".format(config.overrides_url))
elif config.overrides_engine == "vulcan":
	print("[*] - Vulcan login: {}".format(config.vulcan_login))

if config.overrides_stats:
	print("[*] - Statystyki zastępstw: Włączone")
else:
	print("[*] - Statystyki zastępstw: Wyłączone")

if config.overrides_archiver:
	print("[*] - Archiwizacja zastępstw: Włączone")
else:
	print("[*] - Archiwizacja zastępstw: Wyłączone")

if config.timetable_archiver:
	print("[*] - Archiwizacja planu: Włączone")
else:
	print("[*] - Archiwizacja planu: Wyłączone")

if config.ftp_upload:
	print("[*] - FTP Upload: Włączone")
else:
	print("[*] - FTP Upload: Wyłączone")

print("[*] Rozpoczynam działanie\n")

print("[*] Znalazłem {} klas".format(len(timetable.get_units_list())))

for unit in timetable.units:
	print("[*] Przetwarzam plan klasy {}".format(unit), end="")
	timetable.parse_unit(unit)
	print()


target = config.targets[args.target]

#TODO: zbierz zastepstwa
import overrides_parser


print("[*] Uruchamiam eksporter JSON")
output = collections.OrderedDict()
output["_Copyright"] = "2018, Jakub Polgesek"
output["_updateDate_min"] = min(timetable.update_dates)
output["_updateDate_max"] = max(timetable.update_dates)
#output["_updateDate_max"] = "[PREPROD]" #TODO: remove me
output['teachers'] = collections.OrderedDict(sorted(timetable.teachers_timetable.items()))
output['timetable'] = timetable.timetable
output['units'] = timetable.units_list
output['classrooms'] = sorted(timetable.classrooms)


tm = open("teachermap.json", "r")
tm_j = json.loads(tm.read())
tm.close()

tm_j0 = collections.OrderedDict()

# [dluga nazwa] = krotka
for k, v in tm_j.items():
	# del tm_j[k]
	tm_j0[v] = k

#posortuj po dlugiej nazwie
tm_j = collections.OrderedDict(sorted(tm_j0.items()))

tm_j2 = collections.OrderedDict()

# [krotka nazwa] = dluga
for k, v in tm_j.items():
	tm_j2[v] = k

output['teachermap'] = tm_j2


for t in output['teachers']:
	if t not in output['teachermap']:
		output['teachermap'][t] = "{} (brak danych)".format(t)
		print("Brakuje mi nauczyciela {} w teachermap. Sprawdz to.".format(t))

ts = open("timesteps.json", "r")
ts_j = collections.OrderedDict(json.loads(ts.read()))
ts.close()
output['timesteps'] = ts_j

#Hash current timetable before adding timestamp and overrides
output['hash'] = utils.hash_output(json.dumps(output))
print(output['hash'])
output['overrideData'] = overrides_parser.generate()


output['comment'] = "Wyeksportowano "+datetime.now().strftime("%d.%m.%Y %H:%M:%S")
output['_fetch_time'] = datetime.now().strftime("%H:%M")



with open("data.json", "r", encoding="UTF-8") as f:
	temp_data = json.load(f)
	if args.notificationtest:
		print("To jest test powiadomien, wywoluje notifications.start()!")
		try:
			notifications.target = target
			notifications.start(message="main.py --notificationtest 🤔")
		except:
			print("something in notifications failed, check me!")
			pass

	elif temp_data['hash'] != output['hash']:
		print("To jest nowy plan, wywoluje notifications.start()!")
		try:
			notifications.target = target
			notifications.start()
		except:
			print("something in notifications failed, check me!")
			pass


b = open("data.json", "w", encoding="UTF-8")
b.write(json.dumps(output))
b.close()

if output['hash'] != utils.hash_output(json.dumps(output)):
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("!!!! HASHE PLIKU SIĘ NIE ZGADZAJĄ !!!!")
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

print("[*] JSON zapisany do data.json")
if target['ftp_enable']:
	print("[*] Starting FTP Upload to {}".format(target['hostname']))
	ftp = ftplib.FTP(target['hostname'])
	ftp.login(user = target['ftp_user'], passwd = target['ftp_pass'])
	ftp.cwd(target['ftp_rootdir_app'])
	ftp.storbinary('STOR data.json', open("data.json", 'rb'))
	print("[*] Uploaded data.json")

if config.overrides_archiver or config.timetable_archiver:
	if not os.path.exists("archive"):
		os.makedirs(os.path.join("archive", "overrides"))
		os.makedirs(os.path.join("archive", "timetables"))

if config.timetable_archiver:
	archive_filename = datetime.now().strftime("%Y-%m-%d") + "-" + output['hash'] + ".json"

	with open(os.path.join("archive", "timetables", archive_filename), "w") as f:
		f.write(json.dumps(output))
	
	indexer.add_first_known(output)
	indexer.start_indexer()
	
	if target['ftp_enable']:
		ftp.cwd("/")
		ftp.cwd(target['ftp_rootdir_app'])

		try:
			ftp.cwd("data")
		except:
			ftp.mkd("data")

		remotef = ftp.nlst()
		
		for root, dirs, files in os.walk(os.path.join("archive", "timetables"), topdown=True):
			for name in files:
				if name not in remotef or name == "index.json":
					path = os.path.join("archive", "timetables", name)

					try:
						ftp.storbinary('STOR '+name, open(path, 'rb'))
						print("[*] Uploaded {}".format(path))
					except:
						print("[*] Uploaded {}".format(path))
		
		#ftp.cwd('/archive/timetables')
		#ftp.storbinary('STOR '+archive_filename, open(os.path.join("archive", "timetables", archive_filename), 'rb'))
