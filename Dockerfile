# Base Image
FROM python:3.8-alpine
EXPOSE 8001
# RUN apk add --update bash curl git && rm -rf /var/cache/apk/*

COPY docker /usr/src/app
WORKDIR /usr/src/app

RUN pip install -r requirements.txt
CMD python3 run_server.py start