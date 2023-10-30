from flask_restful import Resource

class EventList(Resource):
    def get(self):
        return {'hello': 'from eventlist'}
    
class Event(Resource):
    def get(self, event_id):
        return {'hello': f'from event {event_id}'}