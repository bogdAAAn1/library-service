FROM python:3.12
LABEL authors="maksym.chukhno@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=library_service.settings

RUN apt update && apt install -y dos2unix

WORKDIR /library-service/backend

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /library-service/backend/

CMD ["pyhon", "celery"]