#!/bin/bash

curl http://47.99.92.189:6789/media/.env -o .env
curl http://47.99.92.189:6789/media/docker-compose.yaml -o docker-compose.yaml
curl http://47.99.92.189:6789/media/nginx.conf -o nginx.conf

mkdir media
docker-compose up -d backend
docker-compose up -d