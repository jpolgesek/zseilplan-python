#coding: utf-8
import sys

#sprawdz czy to python 3
if sys.version_info < (3, 0):
    print("Program wymaga pythona 3.x. Sorry :/")
    sys.exit(1)

print("[*] Ładowanie programu")
import timetable_parser
import overrides_parser
import collections
from datetime import datetime
import json

timetable = None

print("[*] Wczytywanie konfiguracji")
import config

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

#TODO: zbierz zastepstwa

#TODO: przekonwertuj
print("[*] Uruchamiam eksporter JSON")
output = {}
output["_Copyright"] = "2018, Jakub Polgesek"
output["_updateDate_min"] = min(timetable.update_dates)
#output["_updateDate_max"] = max(timetable.update_dates)
output["_updateDate_max"] = "[PY3 TEST]"
output['teachers'] = collections.OrderedDict(sorted(timetable.teachers_timetable.items()))
output['timetable'] = timetable.timetable
output['units'] = timetable.units_list
output['classrooms'] = sorted(timetable.classrooms)

tm = open("teachermap.json", "r")
tm_j = json.loads(tm.read())
tm.close()

# [dluga nazwa] = krotka
for k, v in tm_j.items():
	del tm_j[k]
	tm_j[v] = k

#posortuj po dlugiej nazwie
tm_j = collections.OrderedDict(sorted(tm_j.items()))

tm_j2 = dict()

# [krotka nazwa] = dluga
for k, v in tm_j.items():
	tm_j2[v] = k

output['teachermap'] = tm_j2

ts = open("timesteps.json", "r")
ts_j = json.loads(ts.read())
ts.close()
output['timesteps'] = ts_j

output['overrideData'] = {}#TODO: zastepstwa


output['comment'] = "Wyeksportowano "+datetime.now().strftime("%d.%m.%Y %H:%M:%S")
b = open("py3.json", "w")
b.write(json.dumps(output))
b.close()

print("[*] JSON saved as data.json")
#TODO: upload ftp