#!/usr/bin/env python3
#coding: utf-8
import os
import sys
import json
import datetime
import time
import modules.hasher

ARCHIVE_DIR = "archive"


if not os.path.isfile(os.path.join(ARCHIVE_DIR, "internal_index.json")):
	with open(os.path.join(ARCHIVE_DIR, "internal_index.json"), "w", encoding="UTF-8") as f:
		f.write("{}")

def start_indexer():
	known_hashes = []

	with open(os.path.join(ARCHIVE_DIR, "internal_index.json"), "r") as f:
		first_hash_apperances = json.load(f)

	index = {
		"timetable_archives": []
	}

	for r, d, f in os.walk(os.path.join(ARCHIVE_DIR, "timetables")):
		for file in f:
			if ".json" in file and "index" not in file:
				data = None
				with open(os.path.join(r, file), "r") as f:
					data = json.load(f)
				
				temp_date =  data["_updateDate_min"] + data["_updateDate_max"]
				if temp_date.find("<") != -1 or temp_date.find("[") != -1:
					print("This was my internal job, skipping - {}".format(temp_date))
					continue

				if "_fetch_time" not in data:
					data["_fetch_time"] = "00:00"

				if data["hash"] in first_hash_apperances:
					first_hash_apperance = first_hash_apperances[data["hash"]]
				else:
					first_hash_apperance = data['comment'].split("Wyeksportowano ")[1]
				
				index_item = {
					"hash": data["hash"][:8],
					"time": data["_fetch_time"],
					"export_datetime": first_hash_apperance,
					"order_by": time.mktime(datetime.datetime.strptime(first_hash_apperance, "%d.%m.%Y %H:%M:%S").timetuple()),
					"filename": file 
				}

				if data["_updateDate_min"] != data["_updateDate_max"]:
					index_item["date"] = data["_updateDate_min"] + " - " + data["_updateDate_max"]
				else:
					index_item["date"] = data["_updateDate_min"]


				if data["hash"] not in known_hashes:
					index["timetable_archives"].append(index_item)
					known_hashes.append(data["hash"])

	temp = index["timetable_archives"]
	#temp = list(reversed(sorted(temp, key=lambda k: k['export_datetime'])))
	temp = list(reversed(sorted(temp, key=lambda k: k['order_by'])))
	temp[0]['export_datetime'] += " (aktualny)"
	index["timetable_archives"] = temp

	with open(os.path.join(ARCHIVE_DIR, "timetables", "index.json"), "w") as f:
		json.dump(index, f, sort_keys=True)


def add_first_known(output):
	hash = output['hash']
	comment = output['comment']
	with open(os.path.join(ARCHIVE_DIR, "internal_index.json"), "r") as f:
		data = json.load(f)
	
	if hash not in data:
		data[hash] = comment.split("Wyeksportowano ")[1]
		with open(os.path.join(ARCHIVE_DIR, "internal_index.json"), "w") as f:
			json.dump(data, f, sort_keys=True)

	return True

def start_reindexer():
	known_hashes = []

	for r, d, f in os.walk(os.path.join(ARCHIVE_DIR, "timetables")):
		for file in f:
			if ".json" in file and "index" not in file:
				print("Rehashing {}".format(file))

				with open(os.path.join(r, file), "r") as f:
					data = f.read()
				
				data_json = json.loads(data)

				if modules.hasher.hash_output(data) in known_hashes:
					os.remove(os.path.join(r, file))
				else:
					if data_json["hash"] == modules.hasher.hash_output(data):
						print("HASH OK: {}".format(file))
						print(data_json["hash"])
						print(modules.hasher.hash_output(data))
					else:
						print("Fixing hash")
						print("IS:     " + data_json["hash"])
						print("WILL BE:" + modules.hasher.hash_output(data))
						data = data.replace(data_json["hash"], modules.hasher.hash_output(data))
						with open(os.path.join(r, file), "w") as f:
							f.write(data)
					
					known_hashes.append(modules.hasher.hash_output(data))

					


				'''
					
				index_item = {
					"hash": data["hash"][:8],
					"filename": file 
				}

				if data["_updateDate_min"] != data["_updateDate_max"]:
					index_item["date"] = data["_updateDate_min"] + " - " + data["_updateDate_max"]
				else:
					index_item["date"] = data["_updateDate_min"]

				found = False
				for item in index["timetable_archives"]:
					if item["date"] == index_item["date"]:
						found = True
				
				if not found:
					index["timetable_archives"].append(index_item)
				'''

				
	'''
	with open(os.path.join(ARCHIVE_DIR, "timetables", "index.json"), "w") as f:
		json.dump(index, f)
	'''


if __name__ == "__main__":
	start_reindexer()
'''
a = sys.argv[1]

with open("archive\\timetables\\" + a, "r") as f:
	print(modules.hasher.hash_test(f.read()))
'''