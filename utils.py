#coding: utf-8
import hashlib
import json
import sys

def hash_output(output):
	output = json.loads(output)
	hash_input = ""
	hash_input += output["_updateDate_min"] + "," + output["_updateDate_max"]
	hash_input += json.dumps(output['timetable'], sort_keys=True) #Fails reindexing
	#hash_input += json.dumps(output['teachers'], sort_keys=True)  #Fails reindexing
	hash_input += json.dumps(output['units'], sort_keys=True)
	hash_input += json.dumps(output['classrooms'], sort_keys=True)
	hash_input += json.dumps(output['teachermap'], sort_keys=True)
	hash_input += json.dumps(output['timesteps'], sort_keys=True)
	
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	
	return str(hex_dig)

def hash_test(output):
	output = json.loads(output)
	hash_input = output["_updateDate_min"] + "," + output["_updateDate_max"]
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("A: {}".format(hex_dig))
	hash_input = json.dumps(output['timetable'], sort_keys=True) #Fails reindexing
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("B: {}".format(hex_dig))
	hash_input = json.dumps(output['teachers'], sort_keys=True)  #Fails reindexing
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("C: {}".format(hex_dig))
	hash_input = json.dumps(output['units'], sort_keys=True)
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("D: {}".format(hex_dig))
	hash_input = json.dumps(output['classrooms'], sort_keys=True)
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("E: {}".format(hex_dig))
	hash_input = json.dumps(output['teachermap'], sort_keys=True)
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("F: {}".format(hex_dig))
	hash_input = json.dumps(output['timesteps'], sort_keys=True)
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	print("G: {}".format(hex_dig))
	
	return str(hex_dig)


def log(text, end="\n", overwrite = False):
	if overwrite:
		sys.stdout.write('\r')
	sys.stdout.write(text)
	sys.stdout.write(end)
	sys.stdout.flush()

	return True

def step(text, state = "    "):
	if state == "    ":
		log("[{}] {}".format(state, text), end="")
	else:
		log("[{}] {}".format(state, text), overwrite=True)
	
	return True

def debug(text = "", level=2):
	#TODO: check level
	#log(text)
	return True