from re import sub
from unidecode import unidecode
from zseilplan.model.TimetableItem import TimetableItem


class RawTimetableItem:
    def __init__(self, unit: str, day: int, hour: int, html_item):
        self.html_item = html_item
        self.unit = unit
        self.day = day
        self.hour = hour

    def find_by_class(self, object_list, class_name):
        return list(filter(
            lambda obj: obj.className == class_name,
            object_list
        ))
    
    def get_subject(self, parser_object):
        return self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].innerText

    def get_classroom(self, parser_object):
        return self.find_by_class(parser_object.getElementsByTagName("span"),"s")[0].innerText
    
    def get_group2(self, parser_object):
        a = self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].innerText
        b = self.find_by_class(parser_object.getElementsByTagName("span"),"p")[0].parentElement.innerHTML
        
        b = sub(r"<[^>]*>", "", b).split(" ")[0]

        a = a.strip()
        b = b.strip()

        if len(a.split("-")) > 1:
            return a.split("-")[1]
        elif len(b.split("-")) > 1:
            return b.split("-")[1]
        else:
            return '-1'
    

    def get_teacher(self, parser_object):
        #workaroud for timetables, where are duplicate entries for subject, but there are none for teacher
        if len(self.find_by_class(parser_object.getElementsByTagName("span"),"p")) > 1:
            # Try to find teacher_recovery_mapping
            pseudo_teacher = self.find_by_class(parser_object.getElementsByTagName("span"),"p")[1].innerText.upper()
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
            return self.find_by_class(parser_object.getElementsByTagName("span"),"n")[0].innerText.upper()
    
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