FROM python:3.6.5

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py

EXPOSE 8080/tcp

ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=8080"]