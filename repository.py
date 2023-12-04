import json
import os
from flask import current_app, g
import requests
from models import EventModel
from google.cloud import storage
from io import BytesIO
import uuid
import base64
import psycopg2


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
    
    def events_get_by_page(self, pageNumber):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select title, event_description, loc, dat, eventid, image_url, position from event order by title")
            page_size = 4
            page_number = pageNumber
            ps_cursor.scroll((page_number - 1) * page_size)
            paginated_data = ps_cursor.fetchmany(page_size)
            event_list = []
            ps_cursor.execute("SELECT COUNT(*) FROM event")
            # Fetch the total number of records
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
            print(conn)
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select title, event_description, loc, dat, eventid, image_url, position from event where eventid = %s order by title",
                (id,))
            event_record = ps_cursor.fetchone()
            event_model = EventModel(event_record[0], event_record[1], event_record[2], str(event_record[3]),
                                     event_record[4], event_record[5], event_record[6])
            ps_cursor.close()
        return event_model

    def event_add(self, data):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            if 'image_url' in data and data['image_url']:
                image_url = upload_image_to_storage(data['image_url'])
                data['image_url'] = image_url
            else:
                data['image_url'] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/800px-Image_not_available.png?20210219185637"

            if data['loc']:
                lat_lng = self.geocode_location(data['loc'])
                json_data = json.dumps(lat_lng)
                data['position'] = json_data
            ps_cursor.execute(
                "Insert into event (title, event_description, loc, dat, image_url, position) values(%s, %s, %s, %s, %s, %s) returning eventid",
                (data['title'], data['event_description'], data['loc'], data['dat'], data['image_url'], data['position']))
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

