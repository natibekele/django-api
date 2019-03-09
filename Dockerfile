FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
RUN mkdir /app /app/config
WORKDIR /app
COPY ./app /app


COPY ./app/config/requirements.txt /app/config/requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /app/config/requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user
