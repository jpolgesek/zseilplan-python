#!/usr/bin/env python3
from requests import Session
from AdvancedHTMLParser import AdvancedHTMLParser
from collections import OrderedDict
from unidecode import unidecode
import zseilplan.modules.utils
import json
import re


def pprint(txt="",e="\n"):
    if False:
        print(txt, end=e)

# TODO: Share this cls
class TimetableData:
    def __init__(self):
        self.classrooms = []
        self.units = {} # WHY ???
        self.teachers = {}
        self.update_dates = []
        self.timetable = OrderedDict()
        self.teacher_timetable = OrderedDict()
        # self.new_teachers_timetable = OrderedDict()
        self.teacher_recovery = {}
        self.auto_timesteps = []
        self.best_timesteps = []

class RawTimetableItem:
    def __init__(self, unit: str, day: int, hour: int, html_item):
        self.html_item = html_item
        self.unit = unit
        self.day = day
        self.hour = hour


    def find_by_class(self, parser_object, class_name):
        out = []
        for obj in parser_object:
            if obj.className == class_name:
                out.append(obj)
        return out
    
    def get_subject(self, parser_object):
        return self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].innerText

    def get_classroom(self, parser_object):
        return self.find_by_class(parser_object.getElementsByTagName("span"),"s")[0].innerText
    
    def get_group(self, subject):
        if len(subject.split("-")) > 1:
            return subject.split("-")[1]
        else:
            return '-1'
    
    def get_group2(self, parser_object):
        a = self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].innerText
        b = self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].parentElement.innerHTML
        
        b = re.sub(r"<[^>]*>", "", b).split(" ")[0]

        a = a.strip()
        b = b.strip()

        if len(a.split("-")) > 1:
            return a.split("-")[1]
        elif len(b.split("-")) > 1:
            return b.split("-")[1]
        else:
            return '-1'
    

    def get_teacher(self, parser_object):
        # return "Testowy Test"
        #workaroud for timetables, where are duplicate entries for subject, but there are none for teacher
        if len(self.find_by_class(parser_object.getElementsByTagName("span"),"p")) > 1:
            # Try to find teacher_recovery_mapping
            pseudo_teacher = unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"p")[1].innerText.upper())
            return pseudo_teacher
            # if pseudo_teacher in self.teacher_recovery:
            #     return self.teacher_recovery[pseudo_teacher]
            # else:
            #     print("Nie znalazlem recovery dla {}".format(pseudo_teacher))
            #     return pseudo_teacher
        else:
            # pseudo_teacher = unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"n")[0].innerText.upper())
            # if pseudo_teacher in self.teacher_recovery:
            #     return self.teacher_recovery[pseudo_teacher]
            return unidecode(self.find_by_class(parser_object.getElementsByTagName("span"),"n")[0].innerText.upper())
    
    def parse(self):
        item = TimetableItem(
            day = self.day,
            hour = self.hour,
            name = self.get_subject(self.html_item),
            teacher = self.get_teacher(self.html_item),
            classroom = self.get_classroom(self.html_item),
            group = self.get_group2(self.html_item),
            unit = self.unit
        )
        
        return item

class TimetableItem:
    def __init__(self, day: int, hour: int, name: str, teacher: str, classroom: int, unit: str, group: str):
        self.day = day
        self.hour = hour
        self.name = name
        self.teacher = teacher
        self.classroom = classroom
        self.unit = unit
        self.group = group
    
    def __repr__(self):
        return f"<TimetableItem: Day: {self.day} | Hour: {self.hour} | Unit: {self.unit} | Group: {self.group} | Name: {self.name} | Teacher: {self.teacher} | Room: {self.classroom}>"
    
    def serialize(self):
        return {
            "p": self.name,
            "k": self.unit,
            "g": self.group,
            "s": self.classroom,
            "n": self.teacher
        }

class TimetableWWWProvider:
    def __init__(self, url):
        if url.endswith("/"):
            url = url[:-1]
        
        self._url = url
        self._http = Session()
        self._http.encoding = "UTF-8"
        self._units = None
        self.timetable_data = TimetableData()
        self.parser = AdvancedHTMLParser()
    
    def http_get(self, url, encoding = "UTF-8"):
        resp = self._http.get(f"{self._url}/{url}")
        resp.encoding = encoding
        return resp

    def get_units_urls(self) -> list:
        resp = self.http_get("lista.html")

        if resp.status_code != 200:
            raise SystemError(f"Server has returned HTTP {resp.status_code} during download of units. Please check your configuration.")

        self.parser.parseStr(resp.text)
        units = self.parser.getAllNodes().getElementsByTagName("a")

        output = {unit.innerText.upper() : unit.href for unit in units}
        return output

    def get_units(self, url_dict: dict) -> list:
        return sorted(list(url_dict.keys()))

    def import_timesteps(self):
        all_timesteps = []

        for unit in self._units:
            unit_url = self._units[unit]
            resp = self.http_get(unit_url)

            if resp.status_code != 200:
                raise SystemError(f"Server has returned HTTP {resp.status_code} during download of units. Please check your configuration.")

            self.parser.parseStr(resp.text)
            time_blocks = self.parser.getAllNodes().getElementsByClassName("g").getElementsByTagName("td")

            timesteps = []
            for time_block in time_blocks:
                timesteps += list(map(str.strip, time_block.innerText.split("-")))
            
            all_timesteps.append(timesteps)
        
        return all_timesteps
        
    def import_teachers(self):
        print("TODO: Import teachers from full vulcan www")
        for key in self.timetable_data.teacher_timetable.keys():
            self.timetable_data.teachers[key] = f"{key} [NOT IMPLEMENTED]"
        return True
    
    def add_item_to_teacher_timetable(self, item: TimetableItem):
        # If this is the first iteration of this day, create dict
        if item.teacher not in self.timetable_data.teacher_timetable:
            self.timetable_data.teacher_timetable[item.teacher] = {}
        
        # If this is the first iteration of this day, create dict
        if item.day not in self.timetable_data.teacher_timetable[item.teacher]:
            self.timetable_data.teacher_timetable[item.teacher][item.day] = {}
        
        # If this is the first iteration of this lesson in this day, create dict
        if item.hour not in self.timetable_data.teacher_timetable[item.teacher][item.day]:
            self.timetable_data.teacher_timetable[item.teacher][item.day][item.hour] = []
        
        self.timetable_data.teacher_timetable[item.teacher][item.day][item.hour].append(item.serialize())
        return True
    
    def add_item_to_timetable(self, item: TimetableItem):
        if item.classroom not in self.timetable_data.classrooms:
            self.timetable_data.classrooms.append(item.classroom)
        
        # If this is the first iteration of this day, create dict
        if item.day not in self.timetable_data.timetable:
            self.timetable_data.timetable[item.day] = {}
        
        # If this is the first iteration of this lesson in this day, create dict
        if item.hour not in self.timetable_data.timetable[item.day]:
            self.timetable_data.timetable[item.day][item.hour] = {}
        
        # If this is the first iteration of this unit lesson in this day, create array
        if item.unit not in self.timetable_data.timetable[item.day][item.hour]:
            self.timetable_data.timetable[item.day][item.hour][item.unit] = []
        
        self.timetable_data.timetable[item.day][item.hour][item.unit].append(item.serialize())
        self.add_item_to_teacher_timetable(item)
        return True
    
    def import_timetable(self):
        for unit in self._units:
            # self.import_timetable_for_unit(unit_name = unit, unit_url = self._units[unit])
            # continue
            try:
                if not self.import_timetable_for_unit(unit_name = unit, unit_url = self._units[unit]):
                    zseilplan.modules.utils.step("Parsing timetable for {}".format(unit), state="FAIL")
                else:
                    zseilplan.modules.utils.step("Parsing timetable for {}".format(unit), state=" OK ")
            except Exception as e:
                    zseilplan.modules.utils.step("Parsing timetable for {}".format(unit), state="FAIL")
                    print(e)
        
        return True

    def add_raw_item(self, day: int, hour: int, unit: str, raw_item):
        item = RawTimetableItem(unit = unit, 
                                day = day, 
                                hour = hour, 
                                html_item = raw_item)
        return self.add_item_to_timetable(item.parse())

    def parse_single_cell(self, day: int, hour: int, unit: str, cell):
        if cell.getElementsByTagName("span")[0].className == "p":
            zseilplan.modules.utils.debug("Found container with single subject")
            self.add_raw_item(day = day, hour = hour, unit = unit, raw_item = cell)
            return

        zseilplan.modules.utils.debug("Container missing, manual search")

        for parent in cell.getElementsByTagName("span"):
            parent = parent.getChildren()

            if len(parent) == 0:
                continue

            self.add_raw_item(day = day, hour = hour, unit = unit, raw_item = parent)

    def import_timetable_for_unit(self, unit_name, unit_url):
        resp = self.http_get(unit_url)
        if resp.status_code != 200:
            raise SystemError(f"Server has returned HTTP {resp.status_code} during download of single timetable - {unit_name} - {unit_url}. Please check your configuration.")
        
        self.parser.parseStr(resp.text)
        
        # Get update date of this timetable
        update_date = self.parser.getElementsByAttr("align","right")[0][0][0][0].innerText.split('\r\n')[1].split(" ")[1]
        self.timetable_data.update_dates.append(update_date)
        
        rows = self.parser.getAllNodes().getElementsByClassName("tabela")[0].getChildren()

        for hour,row in enumerate(rows):
            columns = row.getElementsByClassName("l")

            for day, column in enumerate(columns):
                #FIXME: Counting from 1...
                day += 1
                
                #Empty - skip
                if column.innerText == "&nbsp;":
                    continue

                zseilplan.modules.utils.debug(f"Day: {day} | Hour: {hour}", level=2)
                entries = column.innerHTML.split("<br />")

                for raw_entry in entries:
                    cell = AdvancedHTMLParser()
                    cell.parseStr(raw_entry)
                    self.parse_single_cell(day = day, hour = hour, unit = unit_name, cell = cell)
        
        return True

    def find_best_timesteps(self):
        current_record = []

        for timestep in self.timetable_data.auto_timesteps[0]:
            if len(timestep) > len(current_record):
                current_record = timestep
        
        self.timetable_data.best_timesteps = current_record
        return
    
    def do_things(self):
        print("Finding units")
        self._units = self.get_units_urls()
        self.timetable_data.units = self.get_units(self._units)

        print("Searching for optimal timesteps")
        z = self.import_timesteps()
        self.timetable_data.auto_timesteps.append(z)
        self.find_best_timesteps()



        self.import_timetable()

        print("Importing teachers")
        z = self.import_teachers()


        with open("test.json", "w", encoding = "UTF-8") as f:
            output = {
                "units": self.timetable_data.units,
                "teachers_new": self.timetable_data.teacher_timetable,
            }
            output["_Copyright"] = "2077, Jakub Polgesek"

            output["_updateDate_min"] = min(self.timetable_data.update_dates)
            output["_updateDate_max"] = max(self.timetable_data.update_dates)

            output['timesteps'] = {"default": self.timetable_data.best_timesteps}
            output['teachers'] = self.timetable_data.teachers
            output['timetable'] = self.timetable_data.timetable
            output['units'] = sorted(self.timetable_data.units)
            output["teachermap"] = self.timetable_data.teachers
            output['classrooms'] = sorted(self.timetable_data.classrooms)

            json.dump(output, f)
        pass