FROM python:3.10-slim-buster

# Fixes "ImportError: libGL.so.1: cannot open shared object file: No such file or directory"
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6

RUN pip install pipenv

WORKDIR /app
COPY Pipfile /app
COPY Pipfile.lock /app

RUN pipenv install --system --deploy

COPY . /app

CMD ./genconf.sh && python app.py --cli