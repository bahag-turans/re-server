from flask import Flask
from flask_restful import Api
from routes import EventList, Event
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_URL = '/api'

api = Api(app)
api.add_resource(EventList, f'{BASE_URL}/events')
api.add_resource(Event, f'{BASE_URL}/event/<event_id>')

@app.route('/')
def hello_world():
    return 'Hello, Flask World!'

if __name__ == '__main__':
            app.run(debug=True)

            