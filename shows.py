# WOBC Show class - Zac Plett 01/24/2019
#
# Takes a JSON array holding the information for an individual show and converts it to a basic
# class with getters to make accessing the show's data fields easier.

class show:

    def __init__(self, json):
        self.data = json
        self.title = self.data['showTitle']
        self.year = self.data['Year']
        self.period = self.data['Period']
        self.day =  self.data['DayOfWeek']
        self.start = self.data["StartTime"]
        self.time = self.data['AssignedLength']
