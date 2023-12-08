import os
from flask import Flask, g, request
from flask_restful import Api

from repository import translate_text
from routes import EventList, Event, Users, PaginatedEventList, UsersFavoriteEvents, UserFavoriteEvents, Comment, \
    EventComments
from flask_cors import CORS
from psycopg2 import pool

# from dotenv import load_dotenv

# load_dotenv() 

BASE_URL = '/api'
HOST = os.environ.get('HOST')
DATABASE = os.environ.get('DATABASE')
DB_PORT = os.environ.get('DB_PORT')
USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')
MIN = os.environ.get('MIN')
MAX = os.environ.get('MAX')

app = Flask(__name__)
CORS(app)

app.config['pSQL_pool'] = pool.SimpleConnectionPool(MIN, MAX, user=USER, password=PASSWORD,
                                                    host=HOST, port=DB_PORT, database=DATABASE)

BASE_URL = '/api'

api = Api(app)
api.add_resource(EventList, f'{BASE_URL}/events')
api.add_resource(Event, f'{BASE_URL}/event/<event_id>')
api.add_resource(Users, f'{BASE_URL}/users', f'{BASE_URL}/users/<userid>')
api.add_resource(PaginatedEventList, f'{BASE_URL}/events/<page_number>')
api.add_resource(Comment, f'{BASE_URL}/comment', f'{BASE_URL}/comment/<commentid>')
api.add_resource(EventComments, f'{BASE_URL}/event/<eventid>/comments')
api.add_resource(UsersFavoriteEvents, f'{BASE_URL}/user/favorite-events')
api.add_resource(UserFavoriteEvents, f'{BASE_URL}/user/<user_id>/favorite-events')


@app.route('/')
def hello_world():
    return 'Hello, Flask World!'


@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('event_description', '')
    location = data.get('loc', '')
    target_lang = request.args.get('target_lang', 'DE')

    translated_title = translate_text(title, target_lang)
    translated_description = translate_text(description, target_lang)
    translated_location = translate_text(location, target_lang)

    data['title'] = translated_title
    data['event_description'] = translated_description
    data['loc'] = translated_location

    return data


@app.teardown_appcontext
def close_conn(e):
    db = g.pop('db', None)
    if db is not None:
        app.config['pSQL_pool'].putconn(db)
        print("Connection returned to the pool")


if __name__ == '__main__':
    app.run(debug=True)
