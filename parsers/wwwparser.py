#coding: utf-8
import requests
from AdvancedHTMLParser import AdvancedHTMLParser
import collections
from unidecode import unidecode
import utils
import json

def pprint(txt="",e="\n"):
	if False:
		print(txt, end=e)

"""
www_parser - module for parsing timetable from vulcan.
"""

class www_parser:
	def __init__(self):
		self.http = requests.Session()
		self.http.encoding = "UTF-8"
		self.base_url = None
		self.classrooms = []
		self.units = {}
		self.update_dates = []
		self.timetable = collections.OrderedDict()
		self.teachers_timetable = collections.OrderedDict()

		try:
			with open("teacher_recovery.json", "r") as f:
				self.teacher_recovery = json.load(f)
		except:
			pass

		return None
	
	def import_teachers(self):
		#print("TODO!")
		return True


	def import_units(self):
		'''
		Gets list of units, that are described in base_url

		returns: bool (True/False)
		'''

		resp = self.http.get("{}/lista.html".format(self.base_url))
		resp.encoding = "UTF-8"

		if resp.status_code != 200:
			print("[E] Serwer zwrócił kod błędu {} przy próbie pobrania listy klas".format(resp.status_code))
			return False

		parser = AdvancedHTMLParser()
		parser.parseStr(resp.text)
		units = parser.getAllNodes().getElementsByTagName("a")

		for unit in units:
			self.units[unit.innerText.upper()] = unit.href
		
		return True

	
	def import_timesteps(self):
		'''
		Gets timesteps from first unit that was found
		'''

		unit_url = next(iter(self.units.values()))
		resp = self.http.get("{}/{}".format(self.base_url, unit_url))
		resp.encoding = "UTF-8"

		if resp.status_code != 200:
			print("[E] Serwer zwrócił kod błędu {} przy próbie pobrania timesteps".format(resp.status_code))
			return False

		parser = AdvancedHTMLParser()
		parser.parseStr(resp.text)
		units = parser.getAllNodes().getElementsByClassName("g").getElementsByTagName("td")

		for unit in units:
			start, stop = unit.innerText.split("-")
		
		# TODO: hold it in some variable
		
		return True


	def find_by_class(self, parser_object, class_name):
		out = []
		for obj in parser_object:
			if obj.className == class_name:
				out.append(obj)
		return out

	def get_teacher(self, parser_object):
		#workaroud for timetables, where are duplicate entries for subject, but there are none for teacher
		if len(self.find_by_class(parser_object.getElementsByTagName("span"),"p")) > 1:
			# Try to find teacher_recovery_mapping
			pseudo_teacher = unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"p")[1].innerText.upper())
			if pseudo_teacher in self.teacher_recovery:
				return self.teacher_recovery[pseudo_teacher]
		else:
			pseudo_teacher = unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"n")[0].innerText.upper())
			if pseudo_teacher in self.teacher_recovery:
				return self.teacher_recovery[pseudo_teacher]
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

	def add_to_teacher_plan(self, p, n, s, unit_name, day, hour):
		if n not in self.teachers_timetable:
		 	self.teachers_timetable[n] = dict()
			
		if day not in self.teachers_timetable[n]:
			self.teachers_timetable[n][day] = dict()
		
		if hour not in self.teachers_timetable[n][day]:
			self.teachers_timetable[n][day][hour] = dict()
		
		self.teachers_timetable[n][day][hour] = {
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

		parser = AdvancedHTMLParser()
		parser.parseStr(resp.text)
		units = parser.getAllNodes().getElementsByTagName("a")
		for unit in self.units:
			self.units[unit.innerText.upper()] = unit.href[7:-5]
			self.units_list.append(unit.innerText.upper())
		return self.units
	
	def import_timetable(self):
		print()

		for unit in self.units:
			if not self.import_timetable_for_unit(unit):
				return False
			else:
				utils.step("Przetwarzam plan lekcji klasy {}".format(unit), state=" OK ")
		
		return True
	
	def import_timetable_for_unit(self, unit_name):
		utils.step("Przetwarzam plan lekcji klasy {}".format(unit_name))
		unit_url = self.units[unit_name]
		
		resp = self.http.get("{}/{}".format(self.base_url, unit_url))
		resp.encoding = "UTF-8"
		if resp.status_code != 200:
			print("[E] Serwer zwrócił kod błędu {} przy próbie pobrania planu klasy {} (url {})".format(resp.status_code, unit_name, unit_url))
			return False
		
		parser = AdvancedHTMLParser()
		parser.parseStr(resp.text)
		
		# Get update date of *this* unit timetable
		self.update_dates.append(parser.getElementsByAttr("align","right")[0][0][0][0].innerText.split('\r\n')[1].split(" ")[1])
		
		rows = parser.getAllNodes().getElementsByClassName("tabela")[0].getChildren()

		for hour,row in enumerate(rows):

			# MAYBE ITS FUCKING TIME TO DECIDE?
			# (and change to count from 0)
			day = 0 #count from 0, because WTF
			#day = 1 #count from 1, because backwards compatibility

			columns = row.getElementsByClassName("l")
			for column in columns:
				day += 1
				
				#Empty - skip
				if column.innerText == "&nbsp;":
					continue

				utils.debug("Dzien {} - {} godzina lekcyjna".format(day, hour), level=2)
				
				'''TODO: make this a func'''

				# If this is the first iteration of this day, create dict
				if day not in self.timetable:
					self.timetable[day] = {}
				
				# If this is the first iteration of this lesson in this day, create dict
				if hour not in self.timetable[day]:
					self.timetable[day][hour] = {}
			
				# If this is the first iteration of this unit lesson in this day, create array
				if unit_name not in self.timetable[day][hour]:
					self.timetable[day][hour][unit_name] = []

				'''END TODO'''


				entries = column.innerHTML.split("<br />")

				for e in entries:
					entry = AdvancedHTMLParser()
					entry.parseStr(e)
					
					if entry.getElementsByTagName("span")[0].className == "p":
						utils.debug("Znaleziono kontener z pojedynczym przedmiotem")

						subject = dict()
						subject["p"] = self.get_subject(entry)
						subject["n"] = self.get_teacher(entry)
						subject["s"] = self.get_classroom(entry)
						subject["g"] = self.get_group(subject["p"])
						
						utils.debug("- Przedmiot: {}".format(subject["p"]))
						utils.debug("- Nauczyciel: {}".format(subject["n"]))
						utils.debug("- Sala: {}".format(subject["s"]))
						utils.debug("- Grupa: {}".format(subject["g"]))

						if subject["s"] not in self.classrooms:
							self.classrooms.append(subject["s"])
						
						self.timetable[day][hour][unit_name].append(subject)
						self.add_to_teacher_plan(subject["p"], subject["n"], subject["s"], unit_name, day, hour)
					else:
						utils.debug("Nie znaleziono kontenera, szukam ręcznie")

						parents = entry.getElementsByTagName("span")
						for parent in parents:
							parent = parent.getChildren()
							if len(parent) != 0:
								subject = dict()
								subject["p"] = parent.getElementsByClassName("p")[0].innerText
								subject["n"] = parent.getElementsByClassName("n")[0].innerText.upper()

								if subject["n"] in self.teacher_recovery:
									subject["n"] = self.teacher_recovery[subject["n"]]

								subject["s"] = parent.getElementsByClassName("s")[0].innerText
								subject["g"] = self.get_group(subject["p"])

								utils.debug("Znaleziono:")
								utils.debug("- Przedmiot: {}".format(subject["p"]))
								utils.debug("- Nauczyciel: {}".format(subject["n"]))
								utils.debug("- Sala: {}".format(subject["s"]))
								utils.debug("- Grupa: {}".format(subject["g"]))

								if subject["s"] not in self.classrooms:
									self.classrooms.append(subject["s"])
								self.timetable[day][hour][unit_name].append(subject)
								self.add_to_teacher_plan(subject["p"], subject["n"], subject["s"], unit_name, day, hour)
		
		return True


	def generate(self):
		units = []

		for unit in self.units:
			units.append(unit)
		self.units = sorted(units)

		self.teachers = collections.OrderedDict(sorted(self.teachers_timetable.items()))
		
		return True