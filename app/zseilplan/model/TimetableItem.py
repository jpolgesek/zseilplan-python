class TimetableItem:
    def __init__(
        self,
        day: int,
        hour: int,
        name: str,
        teacher: str,
        classroom: int,
        unit: str,
        group: str,
    ):
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
            "n": self.teacher,
        }
