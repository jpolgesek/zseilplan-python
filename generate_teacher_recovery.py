#coding: UTF-8
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("www")
parser.add_argument("vulcan")
args = parser.parse_args()

with open(args.www, "r") as f:
    timetable_www = json.load(f)

with open(args.vulcan, "r") as f:
    timetable_vulcan = json.load(f)

teacher_recovery_mapping = {}

week_days = ["UNKNOWN", "Poniedzialek", "Wtorek", "Sroda", "Czwartek", "Piatek"]

for day in timetable_www['timetable']:
    for hour in timetable_www['timetable'][day]:
        for unit in timetable_www['timetable'][day][hour]:
            for lesson in timetable_www['timetable'][day][hour][unit]:
                n = lesson['n']
                if n not in timetable_vulcan['teachermap']:
                    if n not in teacher_recovery_mapping:
                        print()
                        print("Nauczyciel {} prawdopodobnie nie istnieje".format(n))
                        print("Szukam odpowiednika...")

                        unit = unit.upper().strip()
                        
                        if unit not in timetable_vulcan['units']:
                            print("Nie ma klasy {} w danych z vulcana".format(unit))
                            continue
                        else:
                            if day not in timetable_vulcan['timetable']:
                                print("Nie ma dnia {} w danych źródłowych?\n PRZERWANIE PROGRAMU MOŻE BYĆ DOBRĄ OPCJĄ!".format(day))
                                continue
                            if unit not in timetable_vulcan['timetable'][day][hour]:
                                #print("{};{};{};{};{}".format(unit, week_days[int(day)], hour, lesson["p"], lesson["s"]))
                                print("Klasa {} nie ma odpowiadającej lekcji w danych z vulcana (D={}, H={})".format(unit, day, hour))
                                continue
                       
                        try:
                            for vlesson in timetable_vulcan['timetable'][day][hour][unit]:
                                if vlesson['s'] == lesson['s']:
                                    print("Znalazłem: {}".format(vlesson['n']))
                                    teacher_recovery_mapping[n] = vlesson['n']
                        except:
                            print("Nie ma klasy {} w danych vulcana".format(unit))
                        
                        if n not in teacher_recovery_mapping:
                            print("Nie znalazłem: {}".format(n))

with open("teacher_recovery.json", "w", encoding="UTF-8") as f:
    f.write(json.dumps(teacher_recovery_mapping))