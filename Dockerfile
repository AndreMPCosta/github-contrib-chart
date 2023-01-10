FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV APP_HOME=/home/github-contrib-chart

RUN pip install --upgrade pip
RUN pip install pipenv

RUN apt-get update
RUN apt-get -y install nano

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY . $APP_HOME

RUN pipenv install