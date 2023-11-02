from models import EventModel
from flask import Flask
import psycopg2
from psycopg2 import pool
from repository import Repository
from unittest.mock import MagicMock
 
event1 = EventModel('test Sarper dinner', 'not happening', 'Mannheim', '25,OCT,2023',  1)
event2 = EventModel('test Agile practice', 'happening', 'Berlin', '26,OCT,2023',  2)
 
event_row = [
   (event1.title, event1.event_description, event1.loc, event1.dat, event1.eventid),
   (event2.title, event2.event_description, event2.loc, event2.dat, event2.eventid),
]
 
def test_events_get_all():
    app = Flask(__name__)
    with app.app_context():
        p_mock = MagicMock(spec=psycopg2.pool.SimpleConnectionPool)
        app.config['pSQL_pool'] = p_mock
        conn_mock = MagicMock(spec=psycopg2.extensions.connection)
        cursor_mock = MagicMock()
        p_mock.getconn.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = event_row
        repo = Repository()
        events = repo.events_get_all()
        assert events[0].title == event1.title
        assert events[1].eventid == event2.eventid