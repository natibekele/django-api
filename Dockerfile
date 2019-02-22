FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
RUN mkdir /app /app/config
WORKDIR /app
COPY ./app /app


COPY ./app/config/requirements.txt /app/config/requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /app/config/requirements.txt
RUN apk del .tmp-build-deps

RUN adduser -D user
USER user
