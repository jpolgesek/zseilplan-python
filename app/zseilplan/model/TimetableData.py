from collections import OrderedDict


class TimetableData:
    def __init__(self):
        self.classrooms = []
        self.units = {} # WHY ???
        self.teachers = {}
        self.update_dates = []
        self.timetable = OrderedDict()
        self.teacher_timetable = OrderedDict()
        self.teacher_recovery = {}
        self.auto_timesteps = []
        self.best_timesteps = []