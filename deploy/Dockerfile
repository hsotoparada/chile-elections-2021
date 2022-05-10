# pull a light python docker image
FROM python:3.8-slim-buster

# copy required files to the container
RUN mkdir -p /home/app/
COPY deploy/requirements.txt deploy/run_server.sh /home/app/
COPY ./app/app.py ./app/util.py ./app/init.py /home/app/
COPY ./app/data/ /home/app/data
COPY ./app/nginx /home/app/nginx

# set a directory for the app
WORKDIR /home/app

# install dependencies
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends \
     nginx \
  && pip install --upgrade pip setuptools \
  && pip install --no-cache-dir -r requirements.txt \  
  && apt-get purge -y --auto-remove $buildDeps \
  && rm -rf /var/lib/apt/lists/*

RUN pwd && ls -lh . && ls -lh data/ && ls -lh nginx/  

# configure nginx
RUN pwd \
  && cp /home/app/nginx/nginx_chile_elections.conf /etc/nginx/sites-available/nginx_chile_elections.conf \
  && unlink /etc/nginx/sites-enabled/default \
  && ln -v -s /etc/nginx/sites-available/nginx_chile_elections.conf /etc/nginx/sites-enabled \
  && ls -lh /etc/nginx/sites-enabled

# port number the container should expose
EXPOSE 8080

# run script that start nginx and gunicorn when running container
CMD ["bash" , "run_server.sh"]