from flask_restful import Resource
from repository import Repository
from flask import request

repo = Repository()

class EventList(Resource):
    def get(self):
        return [event.__dict__ for event in repo.events_get_all()]
    
class Event(Resource):
    def get(self, event_id):
        return repo.event_get_by_id(int(event_id)).__dict__
    
    def post(self):
        data = request.get_json()
        return repo.event_add(data).__dict__