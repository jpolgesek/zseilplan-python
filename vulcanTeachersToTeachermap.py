#coding: utf-8
import json
import unidecode


with open("teachermap.json", "r", encoding="UTF-8") as f:
	currentJson = json.load(f)

inputFile = open("vulcan_2910.json","r", encoding="UTF-8")
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
			if short.upper() not in currentJson:
				print("Dodaje nowego nauczyciela {}".format(full))
				output[short.upper()] = full
			elif currentJson[short.upper()] != full:
				print("KONFLIKT: ")
				print("Poprzednio: {} {}".format(short.upper(), currentJson[short.upper()]))
				print("Teraz: {} {}".format(short.upper(), full))
				if input("t/n? ").lower() == "t":
					output[short.upper()] = full
			else:
				output[short.upper()] = full
	else:
		print("Niewspierany format, IdLogin={}".format(teacher["IdLogin"]))


with open("teachermap.json", "w", encoding="UTF-8") as f:
	f.write(json.dumps(output))
print("Done.")