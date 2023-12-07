import unittest
from flask import Flask
from flask_restful import Api
from routes import EventList, PaginatedEventList, Event, Users, Comment, EventComments

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(EventList, '/events')
        self.api.add_resource(PaginatedEventList, '/events/<int:page_number>')
        self.api.add_resource(Event, '/events/<int:event_id>')
        self.api.add_resource(Users, '/users')
        self.api.add_resource(Comment, '/comments/<int:commentid>')
        self.api.add_resource(EventComments, '/events/<int:eventid>/comments')

        self.client = self.app.test_client()

    def test_event_list_get(self):
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 500)

    def test_event_list_post(self):
        data = {
            'name': 'Test Event',
            'description': 'This is a test event'
        }
        response = self.client.post('/events', json=data)
        self.assertEqual(response.status_code, 200)

    def test_paginated_event_list_get(self):
        response = self.client.get('/events/2')
        self.assertEqual(response.status_code, 500)
        # ##########3

    def test_event_get(self):
        response = self.client.get('/events/1')
        self.assertEqual(response.status_code, 500)

    def test_event_delete(self):
        response = self.client.delete('/events/1')
        self.assertEqual(response.status_code, 500)

    def test_event_put(self):
        data = {
            'name': 'Updated Event',
            'description': 'This is an updated event'
        }
        response = self.client.put('/events/1', json=data)
        self.assertEqual(response.status_code, 500)

    def test_users_get(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 500)

    def test_users_post(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        response = self.client.post('/users', json=data)
        self.assertEqual(response.status_code, 500)

    def test_users_delete(self):
        response = self.client.delete('/users/1')
        self.assertEqual(response.status_code, 404)

    def test_comment_get(self):
        response = self.client.get('/comments/1')
        self.assertEqual(response.status_code, 500)

    def test_comment_post(self):
        data = {
            'text': 'Test Comment'
        }
        response = self.client.post('/comments/1', json=data)
        self.assertEqual(response.status_code, 500)

    def test_comment_delete(self):
        response = self.client.delete('/comments/1')
        self.assertEqual(response.status_code, 500)

    def test_event_comments_get(self):
        response = self.client.get('/events/1/comments')
        self.assertEqual(response.status_code, 500)

