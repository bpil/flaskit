FROM tiangolo/uwsgi-nginx:python2.7

MAINTAINER Sebastian Ramirez <tiangolo@gmail.com>

RUN pip install flask

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN git clone https://github.com/bpil/jinja2schema.git /jinja2schema
WORKDIR /jinja2schema
RUN python /jinja2schema/setup.py install
# By default, allow unlimited file sizes, modify it to limit the file sizes
# To have a maximum of 1 MB (Nginx's default) change the line to:
# ENV NGINX_MAX_UPLOAD 1m
ENV NGINX_MAX_UPLOAD 0

# Which uWSGI .ini file should be used, to make it customizable
ENV UWSGI_INI /app/uwsgi.ini

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/static

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
# ENV STATIC_INDEX 1
ENV STATIC_INDEX 0

# Copy the entrypoint that will generate Nginx additional configs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Add demo app
#COPY ./app /app
COPY ./ConfigTemplates.py /app/ConfigTemplates.py
COPY ./main.py /app/main.py
COPY ./CustomFilters.py /app/CustomFilters.py
COPY ./templates /app/templates
COPY ./uwsgi.ini /app/uwsgi.ini
WORKDIR /app

CMD ["/usr/bin/supervisord"]
