FROM python:3.8
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
RUN pip install gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app