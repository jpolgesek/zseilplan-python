#!/usr/bin/env python3
import json
from requests import Session
from datetime import datetime

import zseilplan.modules.utils
from AdvancedHTMLParser import AdvancedHTMLParser
from zseilplan.model.TimetableData import TimetableData
from zseilplan.model.TimetableItem import TimetableItem
from zseilplan.model.RawTimetableItem import RawTimetableItem


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

    def http_get(self, url, encoding="UTF-8"):
        resp = self._http.get(f"{self._url}/{url}")
        resp.encoding = encoding
        return resp

    def get_units_urls(self) -> list:
        resp = self.http_get("lista.html")

        if resp.status_code != 200:
            raise SystemError(
                f"Server has returned HTTP {resp.status_code} during download of units. Please check your configuration."
            )

        self.parser.parseStr(resp.text)
        units = self.parser.getAllNodes().getElementsByTagName("a")

        output = {unit.innerText.upper(): unit.href for unit in units}
        return output

    def get_units(self, url_dict: dict) -> list:
        return sorted(list(url_dict.keys()))

    def import_timesteps(self):
        all_timesteps = []

        for unit in self._units:
            unit_url = self._units[unit]
            resp = self.http_get(unit_url)

            if resp.status_code != 200:
                raise SystemError(
                    f"Server has returned HTTP {resp.status_code} during download of units. Please check your configuration."
                )

            self.parser.parseStr(resp.text)
            time_blocks = (
                self.parser.getAllNodes()
                .getElementsByClassName("g")
                .getElementsByTagName("td")
            )

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
        if (
            item.hour
            not in self.timetable_data.teacher_timetable[item.teacher][item.day]
        ):
            self.timetable_data.teacher_timetable[item.teacher][item.day][
                item.hour
            ] = []

        tmp = item.serialize()
        del tmp["g"]  # BUG

        self.timetable_data.teacher_timetable[item.teacher][item.day][item.hour].append(
            tmp
        )
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

        teacher_short = item.teacher
        if teacher_short not in self.timetable_data.teachers:
            self.timetable_data.teachers[
                teacher_short
            ] = f"{teacher_short} (brak danych)"

        tmp = item.serialize()
        del tmp["k"]  # BUG

        self.timetable_data.timetable[item.day][item.hour][item.unit].append(tmp)
        self.add_item_to_teacher_timetable(item)
        return True

    def import_timetable(self):
        for unit in self._units:
            try:
                self.import_timetable_for_unit(
                    unit_name=unit, unit_url=self._units[unit]
                )
                zseilplan.modules.utils.step(
                    "Parsing timetable for {}".format(unit), state=" OK "
                )
            except Exception as e:
                zseilplan.modules.utils.step(
                    "Parsing timetable for {}".format(unit), state="FAIL"
                )
                print(e)

        return True

    def add_raw_item(self, day: int, hour: int, unit: str, raw_item):
        item = RawTimetableItem(unit=unit, day=day, hour=hour, html_item=raw_item)
        return self.add_item_to_timetable(item.parse())

    def parse_single_cell(self, day: int, hour: int, unit: str, cell):
        if cell.getElementsByTagName("span")[0].className == "p":
            zseilplan.modules.utils.debug("Found container with single subject")
            self.add_raw_item(day=day, hour=hour, unit=unit, raw_item=cell)
            return

        zseilplan.modules.utils.debug("Container missing, manual search")

        for parent in cell.getElementsByTagName("span"):
            parent = parent.getChildren()

            if len(parent) == 0:
                continue

            self.add_raw_item(day=day, hour=hour, unit=unit, raw_item=parent)

    def import_timetable_for_unit(self, unit_name, unit_url):
        resp = self.http_get(unit_url)
        if resp.status_code != 200:
            raise SystemError(
                f"Server has returned HTTP {resp.status_code} during download of single timetable - {unit_name} - {unit_url}. Please check your configuration."
            )

        self.parser.parseStr(resp.text)

        # Get update date of this timetable
        # FIXME: What is this [0][0][0][0]
        update_date = (
            self.parser.getElementsByAttr("align", "right")[0][0][0][0]
            .innerText.split("\r\n")[1]
            .split(" ")[1]
        )
        self.timetable_data.update_dates.append(update_date)

        rows = (
            self.parser.getAllNodes().getElementsByClassName("tabela")[0].getChildren()
        )

        for hour, row in enumerate(rows):
            columns = row.getElementsByClassName("l")

            for day, column in enumerate(columns):
                # FIXME: Counting from 1...
                day += 1

                # Empty - skip
                if column.innerText == "&nbsp;":
                    continue

                zseilplan.modules.utils.debug(f"Day: {day} | Hour: {hour}", level=2)
                entries = column.innerHTML.split("<br />")

                for raw_entry in entries:
                    cell = AdvancedHTMLParser()
                    cell.parseStr(raw_entry)
                    self.parse_single_cell(
                        day=day, hour=hour, unit=unit_name, cell=cell
                    )

        return True

    def find_best_timesteps(self):
        best = sorted(self.timetable_data.auto_timesteps[0], key = lambda x: len(x))[-1]
        self.timetable_data.best_timesteps = best
        return True

    def teachermap_load_from_file(self, filename):
        with open(filename, "r", encoding="UTF-8") as f:
            self.timetable_data.teachermap = json.load(f)

        print(f"Using external teachermap: {filename}")
        self.timetable_data.teachers = self.timetable_data.teachermap
        return True

    def do_things(self):
        if len(self.timetable_data.teachers) == 0:
            raise ValueError("Missing teachermap")

        print("Finding units")
        self._units = self.get_units_urls()
        self.timetable_data.units = self.get_units(self._units)

        print("Searching for optimal timesteps")
        self.timetable_data.auto_timesteps.append(self.import_timesteps())
        self.find_best_timesteps()

        timesteps_count = len(self.timetable_data.best_timesteps) // 2
        print(f"Found optimal timesteps, count: {timesteps_count}")

        self.import_timetable()
    
    def add_override_data(self, override_data):
        self.override_data = override_data
        return True

    def get_json(self):
        real_teachers = {k: v for k, v in self.timetable_data.teachers.items() if v.find("brak danych") == -1}
        fake_teachers = {k: v for k, v in self.timetable_data.teachers.items() if v.find("brak danych") != -1}

        sorted_teachers = {k: v for k, v in sorted(real_teachers.items(), key=lambda item: item[1])} 
        sorted_teachers.update({k: v for k, v in sorted(fake_teachers.items(), key=lambda item: item[1])})

        time_string = "Unknown timestamp"

        try:
            time_string = datetime.now().isoformat()
        except:
            pass

        output = {
            "_Copyright":       f"{datetime.now().year}, Jakub Polgesek",
            "comment":          f"Wyeksportowano {time_string}",
            "hash":             "!DEV!",

            "_updateDate_min":  min(self.timetable_data.update_dates),
            "_updateDate_max":  max(self.timetable_data.update_dates),

            "units":            self.timetable_data.units,
            "teachers_new":     self.timetable_data.teacher_timetable,

            "overrideData":     self.override_data,
            "timetable":        self.timetable_data.timetable,
            "teachermap":       sorted_teachers,
            "units":            sorted(self.timetable_data.units),
            "classrooms":       sorted(self.timetable_data.classrooms),
        }

        self.timetable_data.best_timesteps.append("18:25")  # BUG
        self.timetable_data.best_timesteps.append("19:10")  # BUG

        output["timesteps"] = {
            "default": self.timetable_data.best_timesteps
        }

        return output
