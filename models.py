class EventModel:
    def __init__(self, title, description,location, date, id=-1):
        self.title = title
        self.event_description = description
        self.loc = location
        self.dat = date
        self.eventid = id
       