from models import EventModel

event1 = EventModel('Sarper dinner', 'not happening', 'Mannheim', '25,OCT,2023',  1)
event2 = EventModel('Agile practice', 'happening', 'Berlin', '26,OCT,2023',  2)

class Repository():
    def events_get_all(self):
        return [event1, event2]
    
    def event_get_by_id(self, id):
      events=[event1, event2]
      return next((x for x in events if x.id == id), None)
    
    def event_add(self, data):
     return EventModel(data['title'],data['description'],data['location'],data['date'], data['id'])
    