#coding: utf-8
import sys
import time
import utils

#sprawdz czy to python 3
if sys.version_info < (3, 0):
	print("Program wymaga pythona 3.x. Sorry :/")
	sys.exit(1)

if sys.version_info < (3, 7):
	print("Program preferuje pythona 3.7, ale pozwoli się uruchomić na pythonie 3.x")
	print("UWAGA! utils.hash może nie działać poprawnie.")

utils.step("Ładowanie programu")

import collections
from datetime import datetime
import json
import os
import ftplib
import argparse
import indexer 
utils.step("Ładowanie programu", state="FAIL")

import config

import notifications

utils.step("Wczytywanie konfiguracji")
parser = argparse.ArgumentParser()
parser.add_argument("target")
parser.add_argument("--timetable-engine", help="Timetable parser engine (www/vulcan)")
parser.add_argument("--notificationtest", help="Send test notification to all", action="store_true")
args = parser.parse_args()

cfg = config.ConfigFile()
if args.timetable_engine != None:
	cfg.timetable_engine = args.timetable_engine

if not cfg.load_target(args.target):
	utils.step("Wczytywanie konfiguracji", state="FAIL")
	print("[FAIL] Niewłaściwy target: {}".format(args.target))
	print("[FAIL] Właściwe: {}".format(', '.join(config.targets)))
	exit()
else:
	utils.step("Wczytywanie konfiguracji", state=" OK ")
	
cfg.print()

# Create parser object
if cfg.timetable_engine == "www":
	from parsers import wwwparser
	timetable_parser = wwwparser.www_parser()
	timetable_parser.base_url = cfg.timetable_url
elif cfg.timetable_engine == "vulcan":
	from parsers import vulcanparser
	timetable_parser = vulcanparser.vulcan_parser()
	#TODO: change me plz
	with open("vulcan_1309.json", "r", encoding="utf-8") as f:
		timetable_parser.load_data_from_text(f.read())
else:
	print("No such engine '{}'".format(cfg.timetable_engine))
	exit()

import overrides_parser

step_list = [
	{'desc':'Wczytuję oddziały', 				'fn':'import_units',		'engines':['www', 'vulcan']},
	{'desc':'Wczytuję zakres godzin', 			'fn':'import_timesteps',	'engines':['www', 'vulcan']},
	{'desc':'Wczytuję przedmioty',				'fn':'import_subjects',		'engines':['vulcan']},
	{'desc':'Wczytuję sale', 					'fn':'import_classrooms',	'engines':['vulcan']},
	{'desc':'Wczytuję nauczycieli', 			'fn':'import_teachers',		'engines':['www', 'vulcan']},
	{'desc':'Wczytuję grupy', 					'fn':'import_groups',		'engines':['vulcan']},
	{'desc':'Wczytuję plan lekcji', 			'fn':'import_timetable',	'engines':['www', 'vulcan']},
	{'desc':'Przygotowywuję dane do eksportu', 	'fn':'generate',			'engines':['www', 'vulcan']},
]

for step in step_list:
	if cfg.timetable_engine not in step["engines"]:
		# This step does not apply to this engine
		continue
	
	desc = "{} ({}) ".format(step["desc"], step["fn"])
	utils.step(desc)

	result = getattr(timetable_parser, step['fn'])()

	if result:
		utils.step(desc, " OK ")
	else:
		utils.step(desc, "FAIL")
		exit(1)


#TODO: zbierz zastepstwa
import overrides_parser

desc = "Eksportuję dane jako JSON w formacie zseilplanu 2.0"
utils.step(desc)

output = collections.OrderedDict()

# TODO: current year plz
output["_Copyright"] = "2018, Jakub Polgesek"

output["_updateDate_min"] = min(timetable_parser.update_dates)
output["_updateDate_max"] = max(timetable_parser.update_dates)
#output["_updateDate_max"] = "[objectified branch]" #TODO: remove me

output['teachers'] = timetable_parser.teachers
try:
	output['teachers_new'] = timetable_parser.new_teachers
except:
	pass
output['timetable'] = timetable_parser.timetable
output['units'] = timetable_parser.units
output['classrooms'] = sorted(timetable_parser.classrooms)

if cfg.timetable_engine == "www":
	with open("teachermap.json", "r") as f:
		tm_j = json.load(f)

	'''OGARNAC TEN SYF!!!!!!!!!'''

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
		

	for teacher in output['teachers']:
		if teacher not in output['teachermap']:
			output['teachermap'][teacher] = "{} (brak danych)".format(teacher)
			print("Brakuje mi nauczyciela {} w teachermap. Sprawdz to!".format(teacher))

else:
	output['teachermap'] = timetable_parser.teachermap


with open("timesteps.json", "r") as f:
	output['timesteps'] = collections.OrderedDict(json.load(f))


#Hash current timetable before adding timestamp and overrides
output['hash'] = utils.hash_output(json.dumps(output))
print("Hashed {}".format(output['hash']))


output['overrideData'] = overrides_parser.generate()

output['comment'] = "Wyeksportowano "+datetime.now().strftime("%d.%m.%Y %H:%M:%S")
output['_fetch_time'] = datetime.now().strftime("%H:%M")

'''
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
'''

with open("data.json", "w", encoding="UTF-8") as f:
	f.write(json.dumps(output))

if output['hash'] != utils.hash_output(json.dumps(output)):
	# Chyba uwzględnia to zastępstwa :/
	# TODO: Sprawdzić
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("!!!! HASHE PLIKU SIĘ NIE ZGADZAJĄ !!!!")
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

print("[*] JSON zapisany do data.json")
if cfg.target['ftp_enable']:
	print("[*] Starting FTP Upload to {}".format(cfg.target['hostname']))
	ftp = ftplib.FTP(cfg.target['hostname'])
	ftp.login(user = cfg.target['ftp_user'], passwd = cfg.target['ftp_pass'])
	ftp.cwd(cfg.target['ftp_rootdir_app'])
	ftp.storbinary('STOR data.json', open("data.json", 'rb'))
	print("[*] Uploaded data.json")

if cfg.overrides_archiver or cfg.timetable_archiver:
	if not os.path.exists("archive"):
		os.makedirs(os.path.join("archive", "overrides"))
		os.makedirs(os.path.join("archive", "timetables"))

if cfg.timetable_archiver:
	archive_filename = datetime.now().strftime("%Y-%m-%d") + "-" + output['hash'] + ".json"

	with open(os.path.join("archive", "timetables", archive_filename), "w") as f:
		f.write(json.dumps(output))
	
	indexer.add_first_known(output)
	indexer.start_indexer()
	
	if cfg.target['ftp_enable']:
		ftp.cwd("/")
		ftp.cwd(cfg.target['ftp_rootdir_app'])

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
