#!/usr/bin/env python

import os,sys,string,time,json,urllib2
from ConfigTemplates import ConfigTemplate
from glob import glob

from jinja2 import Environment, FileSystemLoader
from jinja2schema import infer, to_json_schema, StringJSONSchemaDraft4Encoder

from flask import Flask, request, make_response, jsonify


app = Flask(__name__)
homedir = '/home/bpilat/dev/flaskit'

mainTemplate = ConfigTemplate(homedir + '/templates')

@app.route('/')
def root():
	response = make_response(jsonify(code='OK', comment='Available apps : /templatize'), 200)
	response.headers['Content-Type'] = 'application/json'
	return response

@app.route('/templatize')
def template_root():
	return mainTemplate.listTemplates()
	
@app.route('/templatize/<template_type>', methods=['GET', 'POST'])
def templatize(template_type):
	response = mainTemplate.responseTemplate(request, template_type)
	return response
