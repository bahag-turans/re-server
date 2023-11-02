from models import EventModel
from flask import request
from routes import EventList, Event
from unittest.mock import MagicMock
from repository import Repository
from app import app

event1 = EventModel('test Sarper dinner', 'not happening', 'Mannheim', '25,OCT,2023',  1)
event2 = EventModel('test Agile practice', 'happening', 'Berlin', '26,OCT,2023',  2)

def test_events_get_all():  
    repo = MagicMock(spec=Repository)
    repo.events_get_all.return_value = [event1, event2]
    events = EventList(repo).get()
    assert events[0]['title'] == 'test Sarper dinner'
    assert events[1]['title'] == 'test Agile practice'


def test_event_add():
    with app.test_request_context():
     repo = MagicMock(spec=Repository)
     req = MagicMock(spec=request)
     data=EventModel('Drilon','Test','Munchen','30,OCT,2023',  3)
     req.get_json.return_value = data
   

# Need to test it -LATER
# def test_book_get():
#     repo = MagicMock(spec=Repository)
#     repo.event_get_by_id.return_value = event1
#     event = EventModel(repo).get(1)
#     assert int(event["id"]) == 1
#     # assert event["title"] == 'test Agile practice'  