import json
import os
from flask import current_app, g ,jsonify
import requests
from models import EventModel, UserModel, UserFavoriteEventsModel, CommentModel, ValidationErrorModel
from google.cloud import storage
from io import BytesIO
import uuid
import base64
import psycopg2
import re

from pubsub import PubSub


def upload_image_to_storage(base64_image):
    storage_client = storage.Client()
    bucket_name = "hub-roitraining01-poc-images"
    folder_name = "event-images"

    filename = f"{str(uuid.uuid4())}.png"

    image_bytes = base64.b64decode(base64_image.split(',')[1])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{folder_name}/{filename}")
    blob.upload_from_file(BytesIO(image_bytes), content_type="image/jpg")

    image_url = blob.public_url

    return image_url
def translate_text(text, target_lang="DE"):
        deepL_url = 'https://api-free.deepl.com/v2/translate'
        headers = {"Authorization": f"DeepL-Auth-Key {os.environ.get('DEEPL_API_KEY')}"}
        print("text: ", text)
        data = {
            "text": [text],
            "target_lang": target_lang
        }


        response = requests.post(deepL_url, json=data, headers=headers)

        print("Response: ", response.__dict__)

        if response.status_code == 200:
            translation = response.json().get('translations')[0].get("text")
            return translation
        else:
            print(f"Translation request failed with status code {response.status_code}")
            return None  

def participate_event(userid, eventid):
    pubsub = PubSub()
    pubsub.participate_event(userid, eventid)

def participate_event(userid, eventid):
    pubsub = PubSub()
    pubsub.participate_event(userid, eventid)

class Repository:
    def get_db(self):
        if 'db' not in g:
            g.db = current_app.config['pSQL_pool'].getconn()
        return g.db

    def events_get_all(self):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select title, event_description, loc, dat, eventid, image_url, position from event order by title")
            event_records = ps_cursor.fetchall()
            event_list = []
            for row in event_records:
                event_list.append(EventModel(
                    row[0], row[1], row[2], str(row[3]), row[4], row[5], row[6]))
            ps_cursor.close()
        print("EVENT LIST: ", event_list)
        return event_list

    def events_get_by_page(self, pageNumber, search_term, sort):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            sql_query = f"SELECT title, event_description, loc, dat, eventid, image_url, position FROM event WHERE title ILIKE %s ORDER BY dat {sort}"
            ps_cursor.execute(sql_query, ('%' + search_term + '%',))
            page_size = 8
            page_number = pageNumber
            if page_number > 1:
                ps_cursor.scroll((page_number - 1) * page_size)
            paginated_data = ps_cursor.fetchmany(page_size)
            event_list = []
            ps_cursor.execute("SELECT COUNT(*) FROM event WHERE title ILIKE %s", ('%' + search_term + '%',))
            total_records = ps_cursor.fetchone()[0]

            total_pages = (total_records + page_size - 1) // page_size

            for row in paginated_data:
                event_list.append(EventModel(
                    row[0], row[1], row[2], str(row[3]), row[4], row[5], row[6]).__dict__)
            ps_cursor.close()
        print("paginated data", event_list)
        response = {
            "data": event_list,
            "total_pages": total_pages,
            "current_page": pageNumber
        }
        return response

    def event_get_by_id(self, id):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select title, event_description, loc, dat, eventid, image_url, position from event where eventid = %s order by title",
                (id,))
            event_record = ps_cursor.fetchone()
            if event_record is None:
                return None

            title = event_record[0]
            description = event_record[1]
            location = event_record[2]

            translated_title = translate_text(title)
            translated_description = translate_text(description)
            translated_location = translate_text(location)

            print("Translated title: ", translated_title)
            print("Translated description: ", translated_description)
            print("Translated location: ", translated_location)

            event_model = EventModel(
                translated_title, translated_description, translated_location , str(event_record[3]),
                event_record[4], event_record[5], event_record[6])

            ps_cursor.close()

        return event_model

    def event_add(self, data):

        for field in ['title', 'event_description', 'loc', 'dat']:
            if field not in data or not data[field]:
                return ValidationErrorModel(f'{field} is required.')    
             
        if not 5 <= len(data['title']) <= 100 or not re.fullmatch(r'^[A-Za-z0-9\s]+$', data['title']):
            return ValidationErrorModel('Title must be 5-100 characters long and contain only alphanumeric characters and spaces.')
        
        if len(data['event_description']) < 10:
            return ValidationErrorModel('Event description must be at least 10 characters long.')
        
        if not re.fullmatch(r'^[A-Za-z0-9\s,]+$', data['loc']):
           return ValidationErrorModel('Location must only contain alphanumeric characters, spaces, and commas.')

        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['dat']):
            return ValidationErrorModel('Invalid date format. Expected YYYY-MM-DD.')
        
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            if 'image_url' in data and data['image_url']:
                image_url = upload_image_to_storage(data['image_url'])
                data['image_url'] = image_url
            else:
                data[
                    'image_url'] = "https://storage.googleapis.com/hub-roitraining01-poc-images/event-images/no-image.jpeg"

            if data['loc']:
                lat_lng = self.geocode_location(data['loc'])
                json_data = json.dumps(lat_lng)
                data['position'] = json_data
            ps_cursor.execute(
                "Insert into event (title, event_description, loc, dat, image_url, position) values(%s, %s, %s, %s, %s, %s) returning eventid",
                (data['title'], data['event_description'], data['loc'], data['dat'], data['image_url'],
                 data['position']))
            conn.commit()
            id = ps_cursor.fetchone()[0]
            ps_cursor.close()
            event = EventModel(data['title'], data['event_description'],
                               data['loc'], data['dat'], id, data['image_url'], data['position'])
            ps_cursor.close()
        return event

    def event_delete(self, id):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute("Delete from event where eventid = %s", (id,))
            conn.commit()
            deleted_rows = ps_cursor.rowcount
            ps_cursor.close()
        return deleted_rows

    def event_update(self, data):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute("update event set title = %s, event_description=%s, loc=%s, dat=%s where eventid = %s",
                              (data['title'], data['event_description'], data['loc'], data['dat'], data['eventid']))
            conn.commit()
            event = EventModel(
                data['title'], data['event_description'], data['loc'], data['dat'], data['eventid'])
            ps_cursor.close()
        return event

    def geocode_location(self, location):
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': location,
            'key': os.environ.get('MAP_API_KEY')
        }
        response = requests.get(base_url, params=params)
        print(response)
        data = response.json()
        lat_lng = {"lat": 0, "lng": 0}
        if (data['results']):
            lat_lng = data['results'][0]['geometry']['location']
        return lat_lng

    def user_get_by_id(self, id):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select full_name, email, phone_number from users where userid = %s",
                (id,))
            user_record = ps_cursor.fetchone()
            if user_record is None:
                return None
            user_model = UserModel(user_record[0], user_record[1], user_record[2], id)
            ps_cursor.close()
        return user_model

    def user_get_by_email(self, email):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select full_name, email, phone_number, userid from users where email = %s",
                (email,))
            user_record = ps_cursor.fetchone()
            if user_record is None:
                return None
            user_model = UserModel(user_record[0], user_record[1], user_record[2], user_record[3])
            ps_cursor.close()
        return user_model

    def user_add(self, data):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            
            name_regex = r'^[A-Za-z\s]+$'
            if ('full_name' not in data or 
            not data['full_name'].strip() or 
            len(data['full_name']) < 2 or 
            not re.fullmatch(name_regex, data['full_name'])):
                return ValidationErrorModel('Invalid name')

            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if ('email' not in data or 
            not data['email'] or 
            not re.fullmatch(email_regex, data['email'])):
                return ValidationErrorModel('Invalid email')

            phone_regex = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            if ('phone_number' not in data or 
            not data['phone_number'] or 
            not re.fullmatch(phone_regex, data['phone_number'])):
                return ValidationErrorModel('Invalid phone number')
            
            ps_cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
            existing_user = ps_cursor.fetchone()
            if existing_user:
                 return ValidationErrorModel('A user with this email already exists.')
                        
            ps_cursor.execute("SELECT * FROM users WHERE phone_number = %s", (data['phone_number'],))
            existing_user = ps_cursor.fetchone()
            if existing_user:
                return ValidationErrorModel('A user with this phone number already exists.')
            
            ps_cursor.execute(
                "Insert into users (full_name, email, phone_number) values(%s, %s, %s) returning userid",
                (data['full_name'], data['email'], data['phone_number']))
            conn.commit()
            id = ps_cursor.fetchone()[0]
            ps_cursor.close()
            user = UserModel(data['full_name'], data['email'], data['phone_number'], id)
            ps_cursor.close()
        return user
    
    def user_delete(self, id):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute("Delete from users where userid = %s", (id,))
            conn.commit()
            deleted_rows = ps_cursor.rowcount
            ps_cursor.close()
        return deleted_rows

    def user_favorite_events_add(self, data):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "Insert into userfavoriteevents (user_id, event_id) values(%s, %s) returning user_id, event_id",
                (data['user_id'], data['event_id']))
            conn.commit()
            user_id, event_id = ps_cursor.fetchone()
            ps_cursor.close()
            user_favorite_event = UserFavoriteEventsModel(user_id, event_id)
            ps_cursor.close()

        return user_favorite_event

    def user_favorite_events_delete(self, data):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "Delete from userfavoriteevents where user_id = %s and event_id = %s", (data['user_id'], data['event_id']))
            conn.commit()
            deleted_rows = ps_cursor.rowcount
            ps_cursor.close()
        return deleted_rows

    def user_favorite_events_get_by_user_id(self, user_id):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select user_id, event_id from userfavoriteevents where user_id = %s",
                (user_id,))
            user_favorite_events_records = ps_cursor.fetchall()
            user_favorite_events_list = []
            for row in user_favorite_events_records:
                user_favorite_events_list.append(UserFavoriteEventsModel(
                    row[0], row[1]).__dict__)
            ps_cursor.close()
        return user_favorite_events_list

    def comment_add(self, data):
             
        required_fields = ['author_name', 'comment', 'dat', 'authorid', 'eventid']
        for field in required_fields:
            if not data.get(field):
                return ValidationErrorModel(f'{field} is required.')           
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "Insert into comment (author_name, comment, dat, authorid, eventid) values(%s, %s, %s, %s, %s) returning commentid",
                (data['author_name'], data['comment'], data['dat'], data['authorid'], data['eventid']))
            conn.commit()
            id = ps_cursor.fetchone()[0]
            ps_cursor.close()
            comment = CommentModel(data['author_name'], data['comment'], data['dat'], data['authorid'],
                                   data['eventid'], id)
            ps_cursor.close()
        return comment

    def get_comments_of_event(self, eventid):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select author_name, comment, dat, authorid, eventid, commentid from comment where eventid = %s",
                (eventid,))
            comment_records = ps_cursor.fetchall()
            comment_list = []
            if comment_records is None:
                return None
            for comment_record in comment_records:
                comment_text = comment_record[1]

                translated_comment_text = translate_text(comment_text)
                comment_list.append(
                    CommentModel(comment_record[0], translated_comment_text, str(comment_record[2]), comment_record[3],
                                 eventid, comment_record[5]))
            ps_cursor.close()
            print("Comment list for eventid: ", eventid, " is: ", comment_list)
        return comment_list

    def comment_get_by_id(self, commentid):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select author_name, comment, dat, authorid, eventid, commentid from comments where commentid = %s",
                (commentid,))
            comment_record = ps_cursor.fetchone()
            if comment_record is None:
                return None

            comment_model = CommentModel(
                comment_record[0], comment_record[1], str(comment_record[2]),
                comment_record[3], comment_record[4], commentid)


            ps_cursor.close()

        return comment_model

    def comment_delete(self, commentid):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute("Delete from comment where commentid = %s", (commentid,))
            conn.commit()
            deleted_rows = ps_cursor.rowcount
            ps_cursor.close()
        return deleted_rows
   
