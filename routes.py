from flask_restful import Resource
from repository import Repository
from flask import request

repository = Repository()


class EventList(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self):
        return [event.__dict__ for event in self.repo.events_get_all()]

    def post(self, req=request):
        data = req.get_json()
        return self.repo.event_add(data).__dict__


class Event(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, event_id):
        return self.repo.event_get_by_id(int(event_id)).__dict__

    def delete(self, event_id):
        return self.repo.event_delete(int(event_id))

    def put(self, event_id, req=request):
        data = req.get_json()
        return self.repo.event_update(data).__dict__
