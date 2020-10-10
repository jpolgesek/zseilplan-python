from datetime import date
import requests
import json
from html import unescape
import datetime
import AdvancedHTMLParser
from unidecode import unidecode

# Placeholder, will be replaced by reference to main cfg object
# This is only to satisfy builtin vs code verifier
try:
    cfg = None
    cfg.teachermap_filename = None
except:
    pass

class OverrideContainer:
    def __init__(self, date_text):
        self.date_text = date_text
        self.day = datetime.datetime.strptime(date_text, "%d.%m.%Y").date().weekday() + 1

        self._overrides = {}
    
    def get_json(self):
        self._overrides["day"] = self.date_text

        return {
            "_max_date": self.date_text,
            "_min_date": self.date_text,
            self.day: self._overrides
        }

    def add_override(self, override_item):
        hour = override_item["hour"]
        unit = override_item["unit"]

        del override_item["unit"]
        del override_item["hour"]

        if hour not in self._overrides:
            self._overrides[hour] = {}

        if unit not in self._overrides[hour]:
            self._overrides[hour][unit] = []
        
        self._overrides[hour][unit].append(override_item)

class OverrideItem:
    pass

class RawOverrideItem:
    def __init__(self, row, teachermap):
        inv_teachermap = {v: k for k, v in teachermap.items()}

        self.hour = row.getChildren()[0].innerText.strip()

        self.old_teacher_long = unidecode(row.getChildren()[1].innerText.strip()) #BUG
        self.new_teacher_long = unidecode(row.getChildren()[5].innerText.strip()) #BUG

        try:
            self.old_teacher_short = inv_teachermap[unidecode(unescape(self.old_teacher_long))]
        except:
            self.old_teacher_short = "-1"
        
        try:
            self.new_teacher_short = inv_teachermap[unidecode(unescape(self.new_teacher_long))]
        except:
            self.new_teacher_short = "-1"
        
        self.subject = row.getChildren()[3].innerText.strip()
        self.classroom = row.getChildren()[4].innerText.strip()

        self.unit = row.getChildren()[2].innerText.strip()
        self.group = None

        self.comments = row.getChildren()[6].innerText.strip()
    
    def parse(self):
        if self.unit.find("IND*") != -1:
            #Indywidualny
            self.unit = self.unit[self.unit.find("IND*"):]
            self.unit = self.unit[4:] #????????
            self.group = -1

        elif len(self.unit.split("|")) == 2:
            self.unit, self.group = self.unit.split("|")
            #Dla konkretnej grupy

        else:
            #Dla całej klasy
            self.group = -1

        if self.group != -1:
            if self.group.find("Grupa-") != -1:
                self.guessedGroup = self.group.split("Grupa-")[1]
            elif self.group.find("r_") != -1:
                self.guessedGroup = self.group.split("r_")[1]
            else:
                self.guessedGroup = -1
        else:
            self.guessedGroup = -1

        if self.new_teacher_long.find("Uczniowie zwolnieni do domu") != -1 or self.new_teacher_long.find("Okienko dla uczni&#243;w") != -1 or self.new_teacher_long.find("Uczniowie przychodz") != -1:
            self.new_teacher_long = -1
            self.new_teacher_short = -1

        output = {
            "hour": self.hour,
            "unit": self.unit,
            "subject": self.subject,
            "s": self.classroom,
            "oldTeacherLong": self.old_teacher_long,
            "newTeacherLong": self.new_teacher_long,
            "oldTeacherShort": self.old_teacher_short,
            "newTeacherShort": str(self.new_teacher_short), #BUG
            "comments": self.comments,
        }

        if self.group != -1:
            output['guessedGroup'] = self.guessedGroup
        
        return output


class HTMLOverrideProvider:
    def __init__(self, url: str):
        if not url.endswith("/"):
            url += "/"
        self.url = url
        self.teachermap = {}
        self.containers2 = {}
        return
    
    def teachermap_load_from_file(self, filename):
        with open(filename, "r", encoding = "UTF-8") as f:
            self.teachermap = json.load(f)
        
        print(f"Using external teachermap: {filename}")
        return True

    def get_overrides_urls(self):
        r = requests.get(self.url)
        r.encoding = "UTF-8"
        if r.status_code != 200:
            return False

        listparser = AdvancedHTMLParser.AdvancedHTMLParser()
        listparser.parseStr(r.text)
        totalOutput = {}

        #FIXME: hack.
        panel = listparser.getElementById("panel_srodkowy_szerszy").getHTML()
        listparser = AdvancedHTMLParser.AdvancedHTMLParser()
        listparser.parseStr(panel)

        for li in listparser.getElementsByTagName("a"):
            url = f"{self.url}{li.href}"
            url = url.replace("\\", "/") # Yes, this happened.

            if not url.endswith(".html"):
                print(f"Skipping: {url} (not a html file)")
                continue

            print(f"Parsing override: {url}")
            self.parse_single_override_file(url)
        
        return self.containers2

    def download_single_override_file(self, url):
        r = requests.get(url)
        r.encoding = "UTF-8"

        if r.status_code != 200:
            print(f"Failed to download: {url} (HTTP {r.status_code})")
            return False
        
        return r.text

    def parse_single_override_file(self, url):
        date_fallback = url.split("-")
        html_content = self.download_single_override_file(url)

        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(html_content)

        for table in parser.getElementsByTagName("table"):
            self.parse_table(table.getChildren(), parser, date_fallback)
            break #Why?
        return
    
    def get_override_date(self, table_element, url): 
        return

    def parse_table(self, table_elements, parser, date_fallback):
        rows = table_elements.getElementsByTagName("tr")
        containers = []
        
        self.current_container = None

        for row in rows:
            is_date_header = len(row.getChildren().getElementsByTagName("th")) == 1
            is_column_header = len(row.getChildren().getElementsByTagName("th")) > 1
            is_data_row = not(is_date_header or is_column_header)

            if is_date_header:
                if self.current_container != None:
                    containers.append(self.current_container.get_json())

                date_text = row.getChildren().getElementsByTagName("th")[0].innerText
                date_text = date_text.split(" ")[1].strip()
                self.current_container = OverrideContainer(date_text)

            elif is_data_row:
                raw_item = RawOverrideItem(row, teachermap = self.teachermap)
                dict_item = raw_item.parse()
                self.current_container.add_override(dict_item)
        
        self.containers2[self.current_container.date_text] = self.current_container.get_json()
        return
        output = {}

        cday = ""
        cdays = []
        for i,row in enumerate(table_elements.getElementsByTagName("tr")):
            if len(row.getChildren()) == 1: #Naglowek (ten z data)
                day = row.getChildren()[i].innerText
                if day.find("Dzie") != -1: #jest w th
                    print("<th>")
                    day = day.split(":")[1]
                    day = day.split("(")[0]
                    day = day.strip()
                elif parser != None: #jest w h1
                    day_ok = False
                    try:
                        print("<h1> - a")
                        day = parser.getElementsByTagName("h1")[0].innerText
                        day = day.split(": ")[1]
                        day = day.split(" (")[0]
                        day = day.strip()
                        temp_fix_check = datetime.datetime.strptime(cday, "%d.%m.%Y").date().weekday() + 1
                        day_ok = True
                    except:
                        print("Fallback, bo ktos edytowal recznie html -.-")

                    if not day_ok:
                        try:
                            print("<h1> - b")
                            day = parser.getElementsByTagName("h1")[1].innerText
                            day = day.split(": ")[1]
                            day = day.split(" (")[0]
                            day = day.strip()
                            temp_fix_check = datetime.datetime.strptime(cday, "%d.%m.%Y").date().weekday() + 1
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
    def search(self):
        urls = self.get_overrides_urls()
        return urls

    def parse(self):
        return

print("SEMI-LEGACY OVERRIDES PARSER!!!!!!!!!")

# def search_for_overrides():
#     r = requests.get("http://www.zseil.edu.pl/zastepstwa/")
#     r.encoding = "UTF-8"
#     if r.status_code != 200:
#         return False
#     listparser = AdvancedHTMLParser.AdvancedHTMLParser()
#     listparser.parseStr(r.text)
#     totalOutput = {}

#     panel = listparser.getElementById("panel_srodkowy_szerszy").getHTML()
#     listparser = AdvancedHTMLParser.AdvancedHTMLParser()
#     listparser.parseStr(panel)

#     for li in listparser.getElementsByTagName("a"):
#         url = "http://www.zseil.edu.pl/zastepstwa/{}".format(li.href)
#         url = url.replace("\\", "/")
#         z = requests.get(url)
#         z.encoding = "UTF-8"
#         if r.status_code != 200:
#             exit(r.status_code)

#         if url.endswith(".html"):
#             print("Zastepstwo w htmlu, parsuje! ({})".format(url))
#             date_fallback = url.split("-")
#             parse_text(totalOutput, z.text, date_fallback)
#     return totalOutput


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
                day_ok = False
                try:
                    print("<h1> - a")
                    day = html_all.getElementsByTagName("h1")[0].innerText
                    day = day.split(": ")[1]
                    day = day.split(" (")[0]
                    day = day.strip()
                    temp_fix_check = datetime.datetime.strptime(cday, "%d.%m.%Y").date().weekday() + 1
                    day_ok = True
                except:
                    print("Fallback, bo ktos edytowal recznie html -.-")

                if not day_ok:
                    try:
                        print("<h1> - b")
                        day = html_all.getElementsByTagName("h1")[1].innerText
                        day = day.split(": ")[1]
                        day = day.split(" (")[0]
                        day = day.strip()
                        temp_fix_check = datetime.datetime.strptime(cday, "%d.%m.%Y").date().weekday() + 1
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
    name = unidecode(unescape(name))
    tm_f = open(cfg.teachermap_filename, "r")
    teachermap = json.loads(tm_f.read())
    for key in teachermap:
        if teachermap[key].lower().find(name.lower()) != -1:
            tm_f.close()
            return key
    tm_f.close()
    return "-1"


# def generate():
#     return search_for_overrides()