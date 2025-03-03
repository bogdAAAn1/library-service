FROM python:3.13.2-slim

LABEL authors="https://github.com/bogdAAAn1/library-service/"

ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y dos2unix

WORKDIR /usr/backend

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

WORKDIR /usr/backend/app

COPY ./backend /usr/backend

COPY ./commands /usr/backend/commands

RUN dos2unix /usr/backend/commands/*.sh
