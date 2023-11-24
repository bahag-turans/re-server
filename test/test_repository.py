from datetime import datetime

from models import EventModel
from flask import Flask
import psycopg2
from psycopg2 import pool
from repository import Repository
from unittest.mock import MagicMock

event1 = EventModel('Test Dinner Event', 'Lorem Ipsum Dorem Lorem Ipsum Dorem', 'Mannheim',
                    datetime(2023, 12, 28, 23, 55, 59), 1, "")
event2 = EventModel('Test Agile practice', 'Lorem Ipsum Dorem Lorem Ipsum Dorem', 'Berlin',
                    datetime(2023, 12, 29, 11, 00, 00), 2, "")
event3 = EventModel('Test Old Event', 'Lorem Ipsum Dorem Lorem Ipsum Dorem', 'Berlin',
                    datetime(2022, 12, 29, 11, 00, 00), 2, "")

event_row = [
    (event1.title, event1.event_description, event1.loc, event1.dat, event1.eventid, event1.image_url),
    (event2.title, event2.event_description, event2.loc, event2.dat, event2.eventid, event2.image_url),
    (event3.title, event3.event_description, event3.loc, event3.dat, event3.eventid, event3.image_url),
]


class TestRepository:
    def setup(self):
        app = Flask(__name__)
        with app.app_context():
            p_mock = MagicMock(spec=psycopg2.pool.SimpleConnectionPool)
            app.config['pSQL_pool'] = p_mock
            conn_mock = MagicMock(spec=psycopg2.extensions.connection)
            cursor_mock = MagicMock()
            p_mock.getconn.return_value = conn_mock
            conn_mock.cursor.return_value = cursor_mock
            return app, cursor_mock

    def test_events_get_all(self):
        app, cursor_mock = self.setup()
        with app.app_context():
            cursor_mock.fetchall.return_value = event_row
            repo = Repository()
            events = repo.events_get_all()
            assert events[0].title == event1.title
            assert events[1].eventid == event2.eventid
            assert events[1].dat == str(event2.dat)

    def test_event_get_by_id(self):
        app, cursor_mock = self.setup()
        with app.app_context():
            cursor_mock.fetchone.return_value = event_row[1]
            repo = Repository()
            event = repo.event_get_by_id(2)
            assert event.title == event2.title
            assert event.eventid == event2.eventid

    def test_event_add(self):
        app, cursor_mock = self.setup()
        with app.app_context():
            event_data = {
                'title': 'New Event',
                'event_description': 'upcoming',
                'loc': 'Mannheim',
                'dat': datetime(2023, 12, 29, 11, 00, 00),
                'image_url': '',
            }
            cursor_mock.execute.return_value = None
            repo = Repository()
            repo.event_add(event_data)
            expected_query = """Insert into event (title, event_description, loc, dat, image_url) values(%s, %s, %s, %s, %s) returning eventid"""
            expected_params = (
                event_data['title'],
                event_data['event_description'],
                event_data['loc'],
                event_data['dat'],
                event_data['image_url'],
            )
            cursor_mock.execute.assert_called_once_with(expected_query, expected_params)

    def test_event_delete(self):
        app, cursor_mock = self.setup()
        with app.app_context():
            cursor_mock.execute.return_value = None
            repo = Repository()
            repo.event_delete(2)
            expected_query = """Delete from event where eventid = %s"""
            expected_params = (
                (2,)
            )
            cursor_mock.execute.assert_called_once_with(expected_query, expected_params)

    def test_event_update(self):
        app, cursor_mock = self.setup()
        with app.app_context():
            event_data = {
                'title': 'Updated Event',
                'event_description': 'upcoming',
                'loc': 'Mannheim',
                'dat': datetime(2023, 12, 29, 11, 00, 00),
                'eventid': 3
            }
            cursor_mock.execute.return_value = None
            repo = Repository()
            repo.event_update(event_data)
            expected_query = """update event set title = %s, event_description=%s, loc=%s, dat=%s where eventid = %s"""
            expected_params = (
                event_data['title'],
                event_data['event_description'],
                event_data['loc'],
                event_data['dat'],
                event_data['eventid']
            )
            cursor_mock.execute.assert_called_once_with(expected_query, expected_params)

