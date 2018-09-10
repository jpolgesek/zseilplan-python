#coding: utf-8
import json
import unidecode


inputFile = open("tm_src.json","r", encoding="UTF-8")
inputJson = json.loads(inputFile.read())["data"]
inputFile.close()

output = {}

for teacher in inputJson:
	if len(teacher["Nazwa"].split("- pracownik")) == 2:
		full = teacher["Nazwa"].split("- pracownik")[0]
		full = unidecode.unidecode(full)
		full, short = full.split("[")
		full = full.strip()
		short = short.strip()[:-1].lower()
		if short != "01": #Vulcan
			#output[short] = [full, "imported.html"]
			output[short.upper()] = full
	else:
		print("Niewspierany format, IdLogin={}".format(teacher["IdLogin"]))


outputFile = open("teachermap.json","w")
outputFile.write(json.dumps(output))
outputFile.close()
print("Done.")