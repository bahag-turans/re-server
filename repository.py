from flask import current_app, g
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
            ps_cursor.execute("select title, event_description, loc, dat, eventid, image_url from event order by title")
            event_records = ps_cursor.fetchall()
            event_list = []
            for row in event_records:
                event_list.append(EventModel(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
            ps_cursor.close()
        print("EVENT LIST: ", event_list)
        return event_list

    def event_get_by_id(self, id):
        conn = self.get_db()
        if conn:
            print(conn)
            ps_cursor = conn.cursor()
            ps_cursor.execute(
                "select title, event_description, loc, dat, eventid, image_url from event where eventid = %s order by title",
                (id,))
            event_record = ps_cursor.fetchone()
            event_model = EventModel(event_record[0], event_record[1], event_record[2], str(event_record[3]),
                                     event_record[4])
            ps_cursor.close()
        return event_model

    def event_add(self, data):
        conn = self.get_db()
        if conn:
            ps_cursor = conn.cursor()
            if 'image_url' in data and data['image_url']:
                image_url = upload_image_to_storage(data['image_url'])
                data['image_url'] = image_url

            ps_cursor.execute(
                "Insert into event (title, event_description, loc, dat, image_url) values(%s, %s, %s, %s, %s) returning eventid",
                (data['title'], data['event_description'], data['loc'], data['dat'], data['image_url']))
            conn.commit()
            id = ps_cursor.fetchone()[0]
            ps_cursor.close()
            event = EventModel(data['title'], data['event_description'], data['loc'], data['dat'], id, data['image_url'])
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
            event = EventModel(data['title'], data['event_description'], data['loc'], data['dat'], data['eventid'])
            ps_cursor.close()
        return event
