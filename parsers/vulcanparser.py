#coding: UTF-8
import json
import collections
import datetime
import config

"""
vulcan_parser - module for parsing timetable from vulcan.
"""

class vulcan_parser:
    json_data = None

    timesteps = {}
    subjects = {}
    classrooms = {}
    units = {}
    teachermap = {}
    teachers = {}
    groups = {}
    units_more = []
    
    timetable = {}
    teachers_timetable = {}

    update_dates = ["VULCAN TEST", "<b><u style='color:white; background: red;'>VULCAN TEST DO NOT USE IN PROD</u></b>"]

    def print(self, text = "", end = "\n", level = 0, indent = 0):
        if indent != 0:
            text = "    - "*indent + text
        print(text, end=end)
        return True

    def load_data_from_text(self, source_text):
        self.json_data = json.loads(source_text)
        return True

    def import_timesteps(self):
        for item in self.json_data["data"]["poryLekcji"]:
            item_id = item["Id"]
            start = item["Poczatek"].split(" ")[1][:-3]
            end = item["Koniec"].split(" ")[1][:-3]

            self.timesteps[item_id] = {
                "start":  start,
                "number": item["Numer"],
                "name":   item["Nazwa"],
                "end":    end
            }

            if config.debug_type == 2:
                self.print("ID: {}, od {} do {}".format(item_id, start, end), indent=1)
            elif config.debug_type == 1:
                self.print(".", end="")
            
        return True

    def import_subjects(self):
        for item in self.json_data["data"]["przedmioty"]:

            self.subjects[item["Id"]] = {
                "global_key":    item["GlobalKey"],
                "short":         item["Kod"],
                "name":          item["Nazwa"],
                "main_topic_id": item["IdPrzedmiotGlowny"]
            }

            #if config.debug_type == 2:
            #    self.print("ID: {}, short: {}".format(item["Id"], item["Kod"]), indent=1)
            #elif config.debug_type == 1:
            #    self.print(".", end="")
        return True

        
    def import_classrooms(self):
        for item in self.json_data["data"]["sale"]:

            self.classrooms[item["Id"]] = {
                "short": item["Kod"]
            }

            if config.debug_type == 2:
                self.print("ID: {}, kod: {}".format(item["Id"], item["Kod"]), indent=1)
            elif config.debug_type == 1:
                self.print(".", end="")
        
        return True

    def import_units(self):
        for item in self.json_data["data"]["oddzialy"]:

            item["Nazwa"] = item["Nazwa"].split(" ")[0]

            self.units[item["IdOddzial"]] = {
                "id_full": item["Id"],
                "level": item["Poziom"],
                "name": item["Nazwa"]
            }

            if config.debug_type == 2:
                self.print("ID: {}, name: {}".format(item["Id"], item["Nazwa"]), indent=1)
            elif config.debug_type == 1:
                self.print(".", end="")

        return True

    def import_teachers(self):
        for item in self.json_data["data"]["pracownicy"]:
            self.teachers[item["Id"]] = {
                "short": item["Kod"].upper(),
                "name": item["DisplayValue"]
            }

            self.teachermap[item["DisplayValue"].split("[")[0]] = item["Kod"].upper()

            if config.debug_type == 2:
                self.print("ID: {}, name: {}".format(item["Id"], item["DisplayValue"]), indent=1)
            elif config.debug_type == 1:
                self.print(".", end="")

        #posortuj po dlugiej nazwie
        self.teachermap = collections.OrderedDict(sorted(self.teachermap.items()))

        # [krotka nazwa] = dluga
        tm_j2 = collections.OrderedDict()
        for k, v in self.teachermap.items():
            #del tm_j[k]
            tm_j2[v] = k

        self.teachermap = collections.OrderedDict()
        for k, v in tm_j2.items():
            self.teachermap[k] = v

        return True

    def import_groups(self):
        for item in self.json_data["data"]["planLekcjiGrupa"]:

            self.groups[item["Id"]] = {
                "short": item["Kod"],
                "name": item["DisplayValue"]
            }

            if config.debug_type == 2:
                self.print("ID: {}, name {}".format(item["Id"], item["DisplayValue"]), indent=1)
            elif config.debug_type == 1:
                self.print(".", end="")

        return True

    def import_timetable(self):
        planLekcji_src = self.json_data["data"]["planLekcji"]

        for item in planLekcji_src:
            
            # Strip time part off
            day = item["Dzien"].split(" ")[0] 
            
            # Parse it as date, and get day of the week
            day = datetime.datetime.strptime(day, "%Y-%m-%d").weekday()

            # Index from 1, not from 0 (I hate myself for this, but I need backwards compat)
            day += 1

            # Get hour number (07:45 => 1)
            hour = self.timesteps[item["IdPoraLekcji"]]["number"]

            # Get unit name
            # Examples: 
            # 4G  - full unit
            # 4KN - individual 
            if item["PseudonimUcznia"] != None:
                unit = item["PseudonimUcznia"] # Individual
                self.units_more.append(unit)
            else:
                unit = self.units[item["IdOddzial"]]["name"].split(" ")[0]



            #todo: co to? docs plz
            if item["IdSala"] == None: 
                item["IdSala"] = 107 

            classroom = self.classrooms[item["IdSala"]]["short"]
            

            if day not in self.timetable: 
                # Create day dict in timetable dict if it's its first occurence
                self.timetable[day] = {} 
            
            if hour not in self.timetable[day]: 
                # Create hour dict in timetable dict if it's its first occurence
                self.timetable[day][hour] = {}
            
            if unit not in self.timetable[day][hour]: 
                # Create unit array in timetable dict if it's its first occurence
                self.timetable[day][hour][unit] = []


            unit_dict = self.timetable[day][hour][unit]
            unit_temp = {}
            

            #unit_temp["ts"] = self.teachers[item["IdPracownik"]]["short"]
            ##unit_temp["tl"] = self.teachers[item["IdPracownik"]]["name"]
            #unit_temp["ss"] = self.subjects[item["IdPrzedmiot"]]["short"]
            ##unit_temp["sl"] = self.subjects[item["IdPrzedmiot"]]["name"]
            #if item["IdPodzial"] != None:
            #    unit_temp["gs"] = self.groups[item["IdPodzial"]]["short"]
            #    #unit_temp["gl"] = self.groups[item["IdPodzial"]]["name"]
            #unit_temp["cl"] = classroom

            #p,s,n,k,g - backwards compatibility
            unit_temp["p"] = self.subjects[item["IdPrzedmiot"]]["short"]
            unit_temp["s"] = classroom
            unit_temp["n"] = self.teachers[item["IdPracownik"]]["short"]
            if item["IdPodzial"] != None:
                unit_temp["g"] = self.groups[item["IdPodzial"]]["short"]
            else:
                unit_temp["g"] = "-1"
            unit_temp["k"] = unit


            #p,s,n,k,g - backwards compatibility
            #unit_temp["p"] = unit_temp["ss"]
            #unit_temp["s"] = unit_temp["cl"]
            #unit_temp["n"] = unit_temp["ts"]
            #unit_temp["k"] = unit
            # unit_dict[item["Id"]]["g"] = unit

            # Add this lesson to unit timetable
            unit_dict.append(unit_temp)


            # Add this lesson to teacher timetable
            short_teacher = self.teachers[item["IdPracownik"]]["short"]

            if short_teacher not in self.teachers_timetable:
                self.teachers_timetable[short_teacher] = {}
            
            if day not in self.teachers_timetable[short_teacher]:
                self.teachers_timetable[short_teacher][day] = {}
            
            if hour not in self.teachers_timetable[short_teacher][day]:
                self.teachers_timetable[short_teacher][day][hour] = {}
            
            self.teachers_timetable[short_teacher][day][hour] = unit_temp
            
            if config.debug_type == 3:
                self.print("---")
                self.print("Dzień {}, godzina lekcyjna {}, klasa {}".format(day, hour, unit))
                self.print("Przedmiot {}".format(unit_temp["subjectShort"]))
                self.print("Nauczyciel {} ({}), sala {}".format(unit_temp["teacherLong"], unit_temp["teacherShort"], unit_temp["classroom"]))

            #self.print(units[item["IdOddzial"]])
            #self.print(timesteps[item["IdPoraLekcji"]])
            #self.print(subjects[item["IdPrzedmiot"]])
            #self.print(teachers[item["IdPracownik"]])
            #self.print(item["IdSala"])
            #self.print(item["IdPodzial"]) #2457 = Indywidualne
            #self.print(item["PseudonimUcznia"])
            #self.print(item["Id"])
            
            if config.debug_type == 2:
                #self.print("ID: {}, name {}".format('0', '0'), indent=1)
                pass
            #elif config.debug_type == 1:
            #    self.print(".", end="")
            
        return True



    def generate(self):
        """ 
        This function will finalize this timetable
        Do NOT change anything after running this

        :returns: True / False
        """

        units = []
        classrooms = []
        subjects = {}
        groups = {}

        for i in self.units_more:
            if i not in units:
                units.append(i)

        for i in self.units:
            if self.units[i]["name"] not in self.units:
                units.append(self.units[i]["name"])
        self.units = sorted(units)

        for i in self.classrooms:
            classrooms.append(self.classrooms[i]["short"])
        self.classrooms = sorted(classrooms)

        for i in self.subjects:
            key = self.subjects[i]["short"]
            name = self.subjects[i]["name"]
            subjects[key] = name
        self.subjects = subjects

        for i in self.groups:
            key = self.groups[i]["short"]
            name = self.groups[i]["name"]
            groups[key] = name
        self.groups = groups

        self.teachers = self.teachers_timetable
        
        return True