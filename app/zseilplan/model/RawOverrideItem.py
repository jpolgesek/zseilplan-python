from html import unescape
from unidecode import unidecode


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
