#!/usr/bin/env python3
#coding: utf-8
import argparse
import json

def compare(input_a, input_b):
	print("------- Compare start -------")
	input_a = json.loads(input_a)
	input_b = json.loads(input_b)
	#input_a["_Copyright"] = "2018, Jakub Polgesek"
	#input_a["_updateDate_min"] = min(timetable.update_dates)
	#input_a["_updateDate_max"] = max(timetable.update_dates)
	#input_a["_updateDate_max"] = "[PY3 TEST]" #TODO: remove me
	##input_a["teachers"] = collections.OrderedDict(sorted(timetable.teachers_timetable.items()))
	#input_a["timetable"] = timetable.timetable
	##input_a["units"] = timetable.units_list
	##input_a["classrooms"] = sorted(timetable.classrooms)

	if input_a["_Copyright"] == input_b["_Copyright"]:
		print("[ OK ] Copyright jest identyczny")
	else:
		print("[ OK ] Copyright różni się")
		
	if sorted(input_a["units"]) == sorted(input_b["units"]):
		if input_a["units"] == input_b["units"]:
			print("[ OK ] Są te same klasy w tej samej kolejności")
		else:
			print("[WARN] Są te same klasy, ale w innej kolejności")
	else:
		print("[FAIL] Są różnice w klasach")
	
	if sorted(input_a["teachermap"]) == sorted(input_b["teachermap"]):
		if input_a["teachermap"] == input_b["teachermap"]:
			print("[ OK ] Są ci sami nauczyciele w tej samej kolejności")
		else:
			print("[WARN] Są ci sami nauczyciele, ale w innej kolejności")
	else:
		print("[FAIL] Są różnice w nauczycielach")
	
	if sorted(input_a["classrooms"]) == sorted(input_b["classrooms"]):
		if input_a["classrooms"] == input_b["classrooms"]:
			print("[ OK ] Są te same sale w tej samej kolejności")
		else:
			print("[WARN] Są te same sale, ale w innej kolejności")
	else:
		print("[FAIL] Są różnice w salach")

	print("Sprawdzam plan lekcji [compat]")
	print("Sprawdzam plan lekcji [TODO!]")
	return
	t_a = input_a["timetable"]
	t_b = input_b["timetable"]
	for day in range(1,6):
		day = str(day)
		if day not in t_b: continue
		for hour in range(1,11):
			hour = str(hour)
			if hour not in t_b[day]: continue
			for unit in t_b[day][hour]:
				for item in t_b[day][hour][unit]:
					print("[lesson]")
					print("P: {}".format(item["p"]))
					print("N: {}".format(item["n"]))
					print("S: {}".format(item["s"]))

	


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-a", help="Pierwszy plik do porównania")
	parser.add_argument("-b", help="Drugi plik do porównania")
	args = parser.parse_args()
	
	input_a = ""
	input_b = ""

	with open(args.a, "r", encoding="UTF-8") as f:
		input_a = f.read()
	
	with open(args.b, "r", encoding="UTF-8") as f:
		input_b = f.read()

	compare(input_a, input_b)