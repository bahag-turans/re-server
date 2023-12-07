from flask_restful import Resource
from repository import Repository, participate_event
from flask import request

repository = Repository()


class EventList(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self):
        return [event.__dict__ for event in self.repo.events_get_all()]

    def post(self, req=request):
        data = req.get_json()
        print("DDDAATTATATTATATATTATATATATTAT")
        print(data)
        return self.repo.event_add(data).__dict__


class PaginatedEventList(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, req=request, page_number=1):
        search_term = req.args.get('search', default='', type=str)
        return self.repo.events_get_by_page(int(page_number), search_term)
    
class UsersFavoriteEvents(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def post(self, req=request):
        data = req.get_json()
        print("DDDAATTATATTATATATTATATATATTAT")
        print(data)
        return self.repo.user_favorite_events_add(data).__dict__
    def delete(self, req=request):
        data = req.get_json()
        return self.repo.user_favorite_events_delete(data)
    

class UserFavoriteEvents(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, user_id):
        return self.repo.user_favorite_events_get_by_user_id(int(user_id))

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

    # This function now only does participate event but I planned to add persisting to DB logic
    # after I see Pub/Sub working
    def post(self, event_id, req=request):
        userid = req.args.get('userid')
        participate_event(userid, event_id)
        return {"message": f"Event participation message acknowledged for user {userid} and event {event_id}"}


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


class Comment(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, commentid):
        comment_model = self.repo.comment_get_by_id(commentid)
        if comment_model is not None:
            return comment_model.__dict__
        else:
            return {"error": f"No user found with commentid {commentid}"}

    def post(self, req=request):
        data = req.get_json()
        return self.repo.comment_add(data).__dict__

    def delete(self, commentid):
        return self.repo.comment_delete(int(commentid))


class EventComments(Resource):
    def __init__(self, repo=repository):
        self.repo = repo

    def get(self, eventid):
        return [comment.__dict__ for comment in self.repo.get_comments_of_event(int(eventid)) if comment is not None]
