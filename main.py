#coding: UTF-8
import modules.utils
modules.utils.check_python_version()



import argparse
parser = argparse.ArgumentParser()
parser.add_argument("target")
parser.add_argument("--timetable-engine", help="Timetable parser engine (www/vulcan)")
parser.add_argument("--vulcan-timetable", help="Vulcan timetable file")
parser.add_argument("--force-notification", help="Force send notification to all", action="store_true")
args = parser.parse_args()

modules.utils.step("Loading program")
import os
import json
import collections
from datetime import datetime
import argparse
modules.utils.step("Loading program", state=" OK ")



modules.utils.step("Loading configuration")
from config import config
cfg = config.Config()

if not cfg.load_target(args.target):
	modules.utils.step("Loading configuration", state="FAIL")
	print("[FAIL] No such target: {}".format(args.target))
	print("[FAIL] Available Targets: {}".format(', '.join(config.targets)))
	exit(1)
else:
	modules.utils.step("Loading configuration", state=" OK ")
	cfg.print()


# Create parser object
if cfg.timetable_engine == "www":
	from parsers import wwwparser
	timetable_parser = wwwparser.www_parser()
	if cfg.teacher_recovery_filename != None:
		timetable_parser.load_teacher_recovery(cfg.teacher_recovery_filename)
	timetable_parser.base_url = cfg.timetable_url
elif cfg.timetable_engine == "vulcan":
	from modules import VulcanAPI
	vapi = VulcanAPI.VulcanAPI()

	modules.utils.step("Vulcan - authentication")
	if vapi.login(cfg.vulcan_login, cfg.vulcan_password):
		modules.utils.step("Vulcan - authentication", state=" OK ")
	else:
		modules.utils.step("Vulcan - authentication", state="FAIL")
		exit()
	
	from parsers import vulcanparser
	timetable_parser = vulcanparser.vulcan_parser()

	timetable = vapi.get_timetable()
	modules.utils.step("Vulcan - downloading timetable")
	if not timetable:
		modules.utils.step("Vulcan - downloading timetable", state="FAIL")
		exit()
	else:
		modules.utils.step("Vulcan - downloading timetable", state=" OK ")
		timetable_parser.load_data_from_text(json.dumps(timetable))
else:
	print("No such timetable engine: {}".format(cfg.timetable_engine))
	exit(1)


step_list = [
	{'desc':'Przetwarzam klasy', 					'fn':'import_units',		'engines':['www', 'vulcan']},
	{'desc':'Przetwarzam zakresy godzin', 			'fn':'import_timesteps',	'engines':['www', 'vulcan']},
	{'desc':'Przetwarzam przedmioty',				'fn':'import_subjects',		'engines':['vulcan']},
	{'desc':'Przetwarzam sale', 					'fn':'import_classrooms',	'engines':['vulcan']},
	{'desc':'Przetwarzam nauczycieli', 				'fn':'import_teachers',		'engines':['www', 'vulcan']},
	{'desc':'Przetwarzam grupy', 					'fn':'import_groups',		'engines':['vulcan']},
	{'desc':'Przetwarzam plan lekcji', 				'fn':'import_timetable',	'engines':['www', 'vulcan']},
	{'desc':'Przygotowuję eksport danych', 			'fn':'generate',			'engines':['www', 'vulcan']},
]


for step in step_list:
	if cfg.timetable_engine not in step["engines"]:
		continue
	
	desc = "{} ({}) ".format(step["desc"], step["fn"])
	modules.utils.step(desc)

	result = getattr(timetable_parser, step['fn'])()

	if result:
		modules.utils.step(desc, " OK ")
	else:
		modules.utils.step(desc, "FAIL")
		exit(1)
	


modules.utils.step("Eksportuję dane jako JSON w formacie zseilplanu 2.0")

output = collections.OrderedDict()

# TODO: current year plz
output["_Copyright"] = "2018, Jakub Polgesek"

output["_updateDate_min"] = min(timetable_parser.update_dates)
output["_updateDate_max"] = max(timetable_parser.update_dates)

output['teachers'] = timetable_parser.teachers
try:
	output['teachers_new'] = timetable_parser.new_teachers
except:
	pass
output['timetable'] = timetable_parser.timetable
output['units'] = sorted(timetable_parser.units)
output['classrooms'] = sorted(timetable_parser.classrooms)

if cfg.timetable_engine == "www":
	with open(cfg.teachermap_filename, "r") as f:
		tm_j = json.load(f)

	'''TODO: OGARNAC TEN SYF!!!!!!!!!'''

	tm_j0 = collections.OrderedDict()

	# [dluga nazwa] = krotka
	for k, v in tm_j.items():
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
			print("Brakuje mi nauczyciela {} w teachermap. Sprawdź to!".format(teacher))

else:
	output['teachermap'] = timetable_parser.teachermap


with open(cfg.timesteps_filename, "r") as f:
	output['timesteps'] = collections.OrderedDict(json.load(f))


#Hash current timetable before adding timestamp and overrides
import modules.hasher
output['hash'] = modules.hasher.hash_output(json.dumps(output))
print("Hashed: {}".format(output['hash']))

import modules.overrides
modules.overrides.cfg = cfg
output['overrideData'] = modules.overrides.generate()

if output['overrideData'] == False:
	print("FAIL - NIE UDAŁO SIĘ POBRAĆ ZASTĘPSTW!")
	output['overrideData'] = {}

output['comment'] = "Wyeksportowano "+datetime.now().strftime("%d.%m.%Y %H:%M:%S")
output['_fetch_time'] = datetime.now().strftime("%H:%M")


if not os.path.exists(cfg.output_data_path):
	os.makedirs(os.path.dirname(cfg.output_data_path), exist_ok=True)
	
with open(cfg.output_data_path, "w", encoding="UTF-8") as f:
	f.write(json.dumps(output))
	print("Zapisano jsona z danymi do {}".format(cfg.output_data_path))

if output['hash'] != modules.hasher.hash_output(json.dumps(output)):
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("!!!! HASHE PLIKU SIĘ NIE ZGADZAJĄ !!!!")
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

uploader = None

if cfg.target["upload"]:
	'''
	if cfg.target["uploader"] == "ftp":
		import modules.upload_ftp
		uploader = modules.upload_ftp.Uploader(cfg.target["hostname"])
		uploader.login(
			cfg.target["ftp"]["user"], 
			cfg.target["ftp"]["pass"]
			)
	elif cfg.target["uploader"] == "scp":
		import modules.upload_scp
		uploader = modules.upload_scp.Uploader(cfg.target["hostname"])
		uploader.login(
			cfg.target["scp"]["user"], 
			cfg.target["scp"]["pass"]
			)
	elif cfg.target["uploader"] == "local":
		import modules.upload_local
		uploader = modules.upload_local.Uploader(cfg.target["hostname"])
	else:
		print("Moduł uploadu {} nie istnieje".format(cfg.target["uploader"]))
		exit(1)
	'''

	uploader = cfg.uploader
	
	
	#FIXME

	uploader.connect()

	uploader.chdir(cfg.target["rootdir_app"])
	uploader.upload_file(cfg.output_data_path, "data.json")


if cfg.overrides_archiver or cfg.timetable_archiver:
	if not os.path.exists("archive"):
		os.makedirs(os.path.join("archive", "overrides"))
		os.makedirs(os.path.join("archive", "timetables"))


if cfg.timetable_archiver:
	archive_filename = datetime.now().strftime("%Y-%m-%d") + "-" + output['hash'] + ".json"

	with open(os.path.join("archive", "timetables", archive_filename), "w") as f:
		f.write(json.dumps(output))
	
	import modules.indexer
	modules.indexer.add_first_known(output)
	modules.indexer.start_indexer()

	if uploader != None:
		
		uploader.connect()

		uploader.chdir(cfg.target["rootdir_app"])
		uploader.mkdir(os.path.join(cfg.target["rootdir_app"], "data"))
		uploader.chdir(os.path.join(cfg.target["rootdir_app"], "data"))
		
		remotef = uploader.ls()
		
		for root, dirs, files in os.walk(os.path.join("archive", "timetables"), topdown=True):
			for name in files:
				if name not in remotef or name == "index.json":
					path = os.path.join("archive", "timetables", name)
					try:
						uploader.upload_file(path, name)
						print("[*] Uploaded {}".format(path))
					except:
						print("[*] Uploaded {}".format(path))


import modules.notifications

notifier = modules.notifications.Notification(cfg, forced=args.force_notification)
