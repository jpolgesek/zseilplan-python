#coding: utf-8
import requests
import AdvancedHTMLParser
import json
import datetime
import html
from unidecode import unidecode

# Placeholder, will be replaced by reference to main cfg object
# This is only to satisfy builtin vs code verifier
try:
	cfg = None
	cfg.teachermap_filename = None
except:
	pass

print("SEMI-LEGACY OVERRIDES PARSER!!!!!!!!!")

def search_for_overrides():
	r = requests.get("http://www.zseil.edu.pl/zastepstwa/")
	r.encoding = "UTF-8"
	if r.status_code != 200:
		return False
	listparser = AdvancedHTMLParser.AdvancedHTMLParser()
	listparser.parseStr(r.text)
	totalOutput = {}
	
	panel = listparser.getElementById("panel_srodkowy_szerszy").getHTML()
	listparser = AdvancedHTMLParser.AdvancedHTMLParser()
	listparser.parseStr(panel)

	for li in listparser.getElementsByTagName("a"):
		url = "http://www.zseil.edu.pl/zastepstwa/{}".format(li.href)
		url = url.replace("\\", "/")
		z = requests.get(url)
		z.encoding = "UTF-8"
		if r.status_code != 200:
			exit(r.status_code)
		
		if url.endswith(".html"):
			print("Zastepstwo w htmlu, parsuje! ({})".format(url))
			date_fallback = url.split("-")
			parse_text(totalOutput, z.text, date_fallback)
	return totalOutput


def parse_text(o, text, date_fallback=None):
	text_parser = AdvancedHTMLParser.AdvancedHTMLParser()
	text_parser.parseStr(text)
	for table in text_parser.getElementsByTagName("table"):
		parse_table(o, table.getChildren(), text_parser, date_fallback)
		break #NIE PARSUJ KOLEJNYCH TABEL


def parse_table(o, table, html_all=None, date_fallback=None):
	output = dict()
	
	cday = ""
	cdays = []
	for i,row in enumerate(table.getElementsByTagName("tr")):
		if len(row.getChildren()) == 1: #Naglowek (ten z data)
			day = row.getChildren()[i].innerText
			if day.find("Dzie") != -1: #jest w th
				print("<th>")
				day = day.split(":")[1]
				day = day.split("(")[0]
				day = day.strip()
			elif html_all != None: #jest w h1
				try:
					print("<h1>")
					day = html_all.getElementsByTagName("h1")[1].innerText
					day = day.split(": ")[1]
					day = day.split(" (")[0]
					day = day.strip()
				except:
					print("Fallback, bo ktos edytowal recznie html -.-")
					day = "{}.{}.{}".format(date_fallback[2],date_fallback[1],date_fallback[0].split("/")[-1])
			else:
				print("Fail, nie znam tego formatu zastepstw")
				return
			
			print("Zastepstwa na dzien {}".format(day))
			cday = day
			cdays.append(day)
		elif len(row.getChildren().getElementsByTagName("th")) == 0: #Nie naglowek (ten z nazwami)
		
			lesson = row.getChildren()[0].innerText.replace("\n","")
			oldTeacher = unidecode(row.getChildren()[1].innerText.replace("\n",""))

			if row.getChildren()[2].innerText.find("IND*") != -1:
				#Indywidualny
				unit = row.getChildren()[2].innerText[row.getChildren()[2].innerText.find("IND*"):].replace("\n","")
				unit = unit[4:]
				group = -1

			elif len(row.getChildren()[2].innerText.split("|")) == 2:
				unit = row.getChildren()[2].innerText.split("|")[0].strip()
				group = row.getChildren()[2].innerText.split("|")[1].strip()
				#Dla konkretnej grupy

			else:
				#Dla całej klasy
				unit = row.getChildren()[2].innerText.strip()
				group = -1
			
			subject = row.getChildren()[3].innerText.strip()
			classroom = row.getChildren()[4].innerText.strip()
			newTeacher = unidecode(row.getChildren()[5].innerText.strip())
			comments = row.getChildren()[6].innerText.strip()

			oldTeacherShort =  unidecode(find_teacher_shortcut(oldTeacher))
			newTeacherShort = find_teacher_shortcut(newTeacher)

			if group != -1:
				if group.find("Grupa-") != -1:
					guessedGroup = group.split("Grupa-")[1]
				elif group.find("r_") != -1:
					guessedGroup = group.split("r_")[1]
				else:
					guessedGroup = -1
			else:
				guessedGroup = -1
			
			if newTeacher.find("Uczniowie zwolnieni do domu") != -1 or newTeacher.find("Okienko dla uczni&#243;w") != -1 or newTeacher.find("Uczniowie przychodz") != -1: #TODO: Uczniowie przychodzą p&#243;źniej
				newTeacher = -1

			#print("[ Zastepstwo ]")
			#print("Godzina: {}".format(lesson))
			#print("Za nauczyciela: {} ({})".format(oldTeacher, oldTeacherShort))
			#print("Klasa: {}".format(unit))
			#print("Grupa: {}".format(group))
			#print("Nowy przedmiot: {}".format(subject))
			#print("Sala: {}".format(classroom))
			#print("Nowy nauczyciel: {} ({})".format(newTeacher, newTeacherShort))
			#print("Uwagi: {}".format(comments))
			#print()
			
			d = datetime.datetime.strptime(cday, "%d.%m.%Y").date().weekday() + 1
			
			if d not in output:
				output[d] = dict()
				output[d]['day'] = cday
			
			if lesson not in output[d]:
				output[d][lesson] = dict()
			if unit not in output[d][lesson]:
				output[d][lesson][unit] = []

			temp = dict()
			temp['subject'] = subject
			temp['s'] = classroom
			temp['oldTeacherLong'] = oldTeacher
			temp['newTeacherLong'] = newTeacher
			temp['oldTeacherShort'] = oldTeacherShort
			temp['newTeacherShort'] = newTeacherShort
			if group != -1:
				temp['guessedGroup'] = guessedGroup
			temp['comments'] = comments

			output[d][lesson][unit].append(temp)
		
	output['_min_date'] = min(cdays)
	output['_max_date'] = max(cdays)

	if max(cdays) in o:
		o[max(cdays)].update(output)
	else:
		o[max(cdays)] = output
	return o


def find_teacher_shortcut(name):
	name = unidecode(html.unescape(name))
	tm_f = open(cfg.teachermap_filename, "r")
	teachermap = json.loads(tm_f.read())
	for key in teachermap:
		if teachermap[key].lower().find(name.lower()) != -1:
			tm_f.close()
			return key
	tm_f.close()
	return "-1"


def generate():
	return search_for_overrides()


#generate()
#with open("zastepstwa.html","r", encoding="UTF-8") as inputData:
#	totalOutput = {}
#	date_fallback = "11.22.3333"
#	parse_text(totalOutput, inputData.read(), date_fallback)
#	#parseZastepstwa(inputData.read())
#inputData.close()