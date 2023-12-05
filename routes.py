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
    
class PaginatedEventList(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, page_number=1):
        return self.repo.events_get_by_page(int(page_number))


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


class Users(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, req=request):
        email = req.args.get('email')
        user_model = self.repo.user_get_by_email(email)
        if user_model is not None:
            return user_model.__dict__
        else:
            return {"error": f"No user found with email {email}"}

    def post(self, req=request):
        data = req.get_json()
        return self.repo.user_add(data).__dict__

    def delete(self, userid):
        return self.repo.user_delete(int(userid))