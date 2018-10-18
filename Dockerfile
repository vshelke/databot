FROM python:3.6.6-slim
LABEL maintainer="vsh046@gmail.com"

WORKDIR /usr/src/app
ADD ./databot/requirements.txt /usr/src/app/requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
ADD databot/ .
ENV FLASK_APP=app.py
EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
