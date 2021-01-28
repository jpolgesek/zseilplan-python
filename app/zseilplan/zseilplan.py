#!/usr/bin/env python3
import argparse
import json

import zseilplan.modules.utils
from zseilplan.modules.TimetableWWWProvider import TimetableWWWProvider
from zseilplan.modules.HTMLOverridesProvider import HTMLOverrideProvider


zseilplan.modules.utils.check_python_version()

parser = argparse.ArgumentParser()
parser.add_argument(
    "action", choices=["timetable", "overrides", "upload", "notification"]
)

parser.add_argument("--teachermap-file", required=False)
parser.add_argument("--output", required=True)
args = parser.parse_args()

ovr = HTMLOverrideProvider("http://www.zseil.edu.pl/zastepstwa/")
if args.teachermap_file:
    ovr.teachermap_load_from_file(args.teachermap_file)

print("Get overrides list")
ovr.search()

print("Parse overrides")
override_output = ovr.parse()


www_provider = TimetableWWWProvider(url="http://www.zseil.edu.pl/rnowa/html/")
www_provider.add_override_data(override_output)

if args.teachermap_file:
    www_provider.teachermap_load_from_file(args.teachermap_file)

www_provider.do_things()
raw_data = www_provider.get_json()

with open(args.output, "w", encoding="UTF-8") as f:
    json.dump(raw_data, f)


def run(*args, **kwargs):
    return True