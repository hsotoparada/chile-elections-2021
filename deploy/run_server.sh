#! /bin/bash

# start nginx
service nginx start
# /usr/sbin/nginx

# start gunicorn
gunicorn --bind :8080 --workers 5 --timeout 1000 --preload app:server