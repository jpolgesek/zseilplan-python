from datetime import datetime


class OverrideContainer:
    def __init__(self, date_text):
        self.date_text = date_text
        self.day = datetime.strptime(date_text, "%d.%m.%Y").date().weekday() + 1

        self._overrides = {}
    
    def get_json(self):
        self._overrides["day"] = self.date_text

        return {
            "_max_date": self.date_text,
            "_min_date": self.date_text,
            self.day: self._overrides
        }

    def add_override(self, override_item):
        # BUG
        hour = override_item["hour"]
        unit = override_item["unit"]

        del override_item["unit"]
        del override_item["hour"]

        if hour not in self._overrides:
            self._overrides[hour] = {}

        if unit not in self._overrides[hour]:
            self._overrides[hour][unit] = []
        
        self._overrides[hour][unit].append(override_item)