FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
RUN mkdir /app /app/config
WORKDIR /app
COPY ./app /app


COPY ./app/config/requirements.txt /app/config/requirements.txt
RUN pip install -r /app/config/requirements.txt

RUN adduser -D user
USER user
