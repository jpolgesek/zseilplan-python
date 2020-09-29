#!/usr/bin/env python3
import os
import json
import argparse
import collections
from datetime import datetime

import zseilplan.modules.utils
from zseilplan.modules.TimetableGenerator import TimetableGenerator
from zseilplan.modules.TimetableWWWProvider import TimetableWWWProvider


zseilplan.modules.utils.check_python_version()

parser = argparse.ArgumentParser()
parser.add_argument("action", choices = [
    "timetable",
    "overrides",
    "upload",
    "notification"
])
args = parser.parse_args()

'''
python run.py timetable
python run.py overrides
python run.py upload
python run.py notification
'''


www_provider = TimetableWWWProvider(url = "http://www.zseil.edu.pl/rnowa/html/")
www_provider.do_things()

# ttgen = TimetableGenerator()
# ttgen.set_provider("www")





def run(*args, **kwargs):
    return True