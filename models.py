class EventModel:
    def __init__(self, title, description, location, date, id=-1, image_url=None, position=None):
        self.title = title
        self.event_description = description
        self.loc = location
        self.dat = date
        self.eventid = id
        self.image_url = image_url
        self.position = position
class UserModel:
    def __init__(self, full_name, email=None, phone_number=None, id=-1, favorite_events=None):
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.userid = id

class ValidationErrorModel:
    def __init__(self, error_message):
        self.error=error_message

class CommentModel:
    def __init__(self, author_name, comment, date, authorid, eventid, commentid=-1):
        self.author_name = author_name
        self.comment = comment
        self.date = date
        self.authorid = authorid
        self.eventid = eventid
        self.commentid = commentid
class UserFavoriteEventsModel:
    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id
