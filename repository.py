from flask import current_app, g
from models import EventModel
import psycopg2

event1 = EventModel('Sarper dinner', 'not happening', 'Mannheim', '25,OCT,2023',  1)
event2 = EventModel('Agile practice', 'happening', 'Berlin', '26,OCT,2023',  2)

class Repository():
    def get_db(self):
        if 'db' not in g:
                g.db = current_app.config['pSQL_pool'].getconn()
        return g.db

    def events_get_all(self):
      conn = self.get_db()
      if(conn):
        print(conn)
        ps_cursor = conn.cursor()
        ps_cursor.execute("select title, event_description, loc, dat, eventid from event order by title")
        event_records = ps_cursor.fetchall()
        event_list = []
        for row in event_records:
            event_list.append(EventModel(row[0], row[1], row[2], str(row[3]), row[4]))
        ps_cursor.close()
      print("EVENT LIST: " , event_list)
      return event_list
    
    def event_get_by_id(self, id):
      conn = self.get_db()
      if(conn):
        print(conn)
        ps_cursor = conn.cursor()
        ps_cursor.execute("select title, event_description, loc, dat, eventid from event where eventid = %s order by title", (id,))
        event_record = ps_cursor.fetchone()
        event_model = EventModel(event_record[0], event_record[1], event_record[2], str(event_record[3]), event_record[4])
        ps_cursor.close()
      return event_model
    
    def event_add(self, data):
      conn = self.get_db()
      if(conn):
        print(conn)
        ps_cursor = conn.cursor()
        ps_cursor.execute("Insert into event (title, event_description, loc, dat) values(%s, %s, %s, %s) returning eventid", (data['title'],data['description'],data['location'],data['date']))
        conn.commit()
        id = ps_cursor.fetchone()[0]
        ps_cursor.close()
        event = EventModel(data['title'],data['description'],data['location'],data['date'], id)
        ps_cursor.close()
      return event
    