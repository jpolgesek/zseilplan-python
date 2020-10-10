#!/usr/bin/env python3
import argparse

import zseilplan.modules.utils
from zseilplan.modules.TimetableGenerator import TimetableGenerator
from zseilplan.modules.TimetableWWWProvider import TimetableWWWProvider
from zseilplan.modules.HTMLOverridesProvider import HTMLOverrideProvider


zseilplan.modules.utils.check_python_version()

parser = argparse.ArgumentParser()
parser.add_argument("action", choices = [
    "timetable",
    "overrides",
    "upload",
    "notification"
])

parser.add_argument("--teachermap-file", required = False)
args = parser.parse_args()

ovr = HTMLOverrideProvider("http://www.zseil.edu.pl/zastepstwa/")
if args.teachermap_file:
    ovr.teachermap_load_from_file(args.teachermap_file)
override_output = ovr.search()


www_provider = TimetableWWWProvider(url = "http://www.zseil.edu.pl/rnowa/html/")
www_provider.oo = override_output
if args.teachermap_file:
    www_provider.teachermap_load_from_file(args.teachermap_file)

www_provider.do_things()


def run(*args, **kwargs):
    return True