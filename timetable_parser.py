#coding: utf-8
import requests
import AdvancedHTMLParser
import collections
from unidecode import unidecode

def pprint(txt="",e="\n"):
	if False:
		print(txt, end=e)

class www_parser:
	def __init__(self, base_url):
		self.http = requests.Session()
		self.http.encoding = "UTF-8"
		self.base_url = base_url
		self.classrooms = []
		self.units = collections.OrderedDict()
		self.units_list = []
		self.update_dates = []
		self.timetable = collections.OrderedDict()
		self.teachers_timetable = collections.OrderedDict()

		return None
	
	def find_by_class(self, parser_object, class_name):
		out = []
		for obj in parser_object:
			if obj.className == class_name:
				out.append(obj)
		return out

	def get_teacher(self, parser_object):
		#workaroud for timetables, where are duplicate entries for subject, but there are none for teacher
		if len(self.find_by_class(parser_object.getElementsByTagName("span"),"p")) > 1:
			return unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"p")[1].innerText.upper())
		else:
			return unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"n")[0].innerText.upper())

	def get_subject(self, parser_object):
		return self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].innerText

	def get_classroom(self, parser_object):
		return self.find_by_class(parser_object.getElementsByTagName("span"),"s")[0].innerText
	
	def get_group(self, subject):
		if len(subject.split("-")) > 1:
			return subject.split("-")[1]
		else:
			return '-1'

	def add_to_teacher_plan(self, p, n, s, unit_name, day, i):
		if n not in self.teachers_timetable:
		 	self.teachers_timetable[n] = dict()
			
		if day not in self.teachers_timetable[n]:
			self.teachers_timetable[n][day] = dict()
		
		if i not in self.teachers_timetable[n][day]:
			self.teachers_timetable[n][day][i] = dict()
		
		self.teachers_timetable[n][day][i] = {
			"p":p,
			"n":n.upper(),
			"s":s, 
			"k":unit_name
		}
				
		return

	def get_units_list(self):
		'''Returns list of units, that are described in currently set timetable url'''

		resp = self.http.get("{}/lista.html".format(self.base_url))
		resp.encoding = "UTF-8"
		if resp.status_code != 200:
			print("[E] Serwer zwrócił kod błędu {} przy próbie pobrania listy klas".format(resp.status_code))
			exit(-1)

		parser = AdvancedHTMLParser.AdvancedHTMLParser()
		parser.parseStr(resp.text)
		units = parser.getAllNodes().getElementsByTagName("a")
		for unit in units:
			self.units[unit.innerText.upper()] = unit.href[7:-5]
			self.units_list.append(unit.innerText.upper())
		return self.units
	
	def parse_unit(self, unit_name):
		unit_id = self.units[unit_name]
		
		resp = self.http.get("{}/plany/o{}.html".format(self.base_url, unit_id))
		resp.encoding = "UTF-8"
		if resp.status_code != 200:
			print("[E] Serwer zwrócił kod błędu {} przy próbie pobrania planu klasy {} (id {})".format(resp.status_code, unit_name, unit_id))
			exit(-1)
		
		parser = AdvancedHTMLParser.AdvancedHTMLParser()
		parser.parseStr(resp.text)
		
		#get update date
		# self.update_dates[unit_name] = parser.getElementsByAttr("align","right")[0][0][0][0].innerText.split('\r\n')[1].split(" ")[1]
		self.update_dates.append(parser.getElementsByAttr("align","right")[0][0][0][0].innerText.split('\r\n')[1].split(" ")[1])
		

		rows = parser.getAllNodes().getElementsByClassName("tabela")[0].getChildren()

		for i,row in enumerate(rows):
			day = 0 #count from 0, because WTF
			#day = 1 #count from 1, because backwards compatibility
			columns = row.getElementsByClassName("l")
			for column in columns:
				day += 1
				#print("Dzien {} - {} godzina lekcyjna".format(day, i))
				print(".",end="")
				
				'''TODO: make this a func'''

				#Empty - skip
				if column.innerText == "&nbsp;":
					continue

				#If this is the first iteration of this day, create dict
				if day not in self.timetable:
					self.timetable[day] = dict()
				
				#If this is the first iteration of this lesson in this day, create dict
				if i not in self.timetable[day]:
					self.timetable[day][i] = dict()
			
				#If this is the first iteration of this unit lesson in this day, create dict
				if unit_name not in self.timetable[day][i]:
					self.timetable[day][i][unit_name] = []


				'''END TODO'''

				entries = column.innerHTML.split("<br />")
				for e in entries:
					entry = AdvancedHTMLParser.AdvancedHTMLParser()
					entry.parseStr(e)
					if entry.getElementsByTagName("span")[0].className == "p":
						pprint()
						pprint("[D] Znaleziono kontener z pojedynczym przedmiotem")

						subject = dict()
						subject["p"] = self.get_subject(entry)
						subject["n"] = self.get_teacher(entry)
						subject["s"] = self.get_classroom(entry)
						subject["g"] = self.get_group(subject["p"])
						
						pprint("[D] - Przedmiot: {}".format(subject["p"]))
						pprint("[D] - Nauczyciel: {}".format(subject["n"]))
						pprint("[D] - Sala: {}".format(subject["s"]))
						pprint("[D] - Grupa: {}".format(subject["g"]))


						if subject["s"] not in self.classrooms:
							self.classrooms.append(subject["s"])
						
						self.timetable[day][i][unit_name].append(subject)
						self.add_to_teacher_plan(subject["p"], subject["n"], subject["s"], unit_name, day, i)
					else:
						pprint()
						pprint("[D] Nie znaleziono kontenera, szukam ręcznie")

						parents = entry.getElementsByTagName("span")
						for parent in parents:
							parent = parent.getChildren()
							if len(parent) != 0:
								pprint("[D] - Znaleziono:")
								subject = dict()
								subject["p"] = parent.getElementsByClassName("p")[0].innerText
								subject["n"] = parent.getElementsByClassName("n")[0].innerText.upper()
								subject["s"] = parent.getElementsByClassName("s")[0].innerText
								subject["g"] = self.get_group(subject["p"])
								pprint("[D]   - Przedmiot: {}".format(subject["p"]))
								pprint("[D]   - Nauczyciel: {}".format(subject["n"]))
								pprint("[D]   - Sala: {}".format(subject["s"]))
								pprint("[D]   - Grupa: {}".format(subject["g"]))
								if subject["s"] not in self.classrooms:
									self.classrooms.append(subject["s"])
								self.timetable[day][i][unit_name].append(subject)
								self.add_to_teacher_plan(subject["p"], subject["n"], subject["s"], unit_name, day, i)
