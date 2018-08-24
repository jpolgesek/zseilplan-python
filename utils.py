#coding: utf-8
import hashlib
import json


def hash_output(output):
	hash_input = ""
	hash_input += output["_updateDate_min"] + "," + output["_updateDate_max"]
	hash_input += json.dumps(output['timetable'])
	hash_input += ",".join(output['teachers'])
	hash_input += ",".join(output['units'])
	hash_input += ",".join(output['classrooms'])
	hash_input += ",".join(output['teachermap'])
	hash_input += ",".join(output['timesteps'])
	
	hash_object = hashlib.sha256(hash_input.encode("UTF-8"))
	hex_dig = hash_object.hexdigest()
	
	return str(hex_dig)