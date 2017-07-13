# flaskit

REST jinja API

## Installation 

### Requirements :
* jinja2 - pip install jinja2
* flask - pip install flask

### Install steps
Clone repository
Put templates in /templates directory with .j2 extension

## Utilisation :

### Server
Launch the Flask server :
export FLASK_APP=flaskit.py
flask run -p <port_number>

### Client
GET /templatize
will return the list of available templates in /templates directory, in json

GET /templatize/<template_name>
will return a json describing the parameters needed for the template

POST /templatise/<template_name>
with template parameters as json will return a json containing the rendered template
