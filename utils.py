#coding: utf-8
import hashlib
import json


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