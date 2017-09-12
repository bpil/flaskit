#!/usr/bin/env python

import os,sys,string,time,json,urllib2
from ConfigTemplates import ConfigTemplate
from glob import glob

from jinja2 import Environment, FileSystemLoader
from jinja2schema import infer, to_json_schema, StringJSONSchemaDraft4Encoder

from flask import Flask, request, make_response, jsonify
from flask.views import MethodView


app = Flask(__name__)
homedir = '/app'

mainTemplate = ConfigTemplate(homedir + '/templates')

@app.route('/')
def root():
	response = make_response(jsonify(code='OK', comment='Available apps : /templatize'), 200)
	response.headers['Content-Type'] = 'application/json'
	return response

@app.route('/templatize')
def template_root():
	mainTemplate.refresh()
	r = mainTemplate.listTemplates()
	response = make_response(jsonify(r['data']), r['code'])
	response.headers['Content-Type'] = 'application/json'
	return response
	
@app.route('/templatize/<template_type>', methods=['GET', 'POST'])
def templatize(template_type):
	if request.method == 'GET':
		r = mainTemplate.getTemplate(template_type)
		response = make_response(jsonify(r['data']), r['code'])
		response.headers['Content-Type'] = 'application/json'
		return response
	if request.method == 'POST':
		r = mainTemplate.postTemplate(request, template_type)
		response = make_response(jsonify(r['data']['config']), r['code'])
		response.headers['Content-Type'] = 'application/json'
		return response
	return mainTemplate.errorCode('Wrong Method')
#	response = mainTemplate.responseTemplate(request, template_type)
#	return response




"""
class configAPI(MethodView):

	def __init__(self, templateDir):
		self.mainTemplate = ConfigTemplate(templateDir)

	def get(self, template_type):
		if template_type is None:
			return self.mainTemplate.listTemplates()
		else:
			return self.mainTemplate.getTemplate(template_type)

	def post(self, template_type):
		return self.mainTemplate.postTemplate(request, template_type)

obj_API = configAPI(homedir + '/templates')
config_view = obj_API.as_view('config_view')
app.add_url_rule('/templatize/', defaults={'template_type': None}, view_func=config_view, methods=['GET', ])
app.add_url_rule('/templatize/<template_type>', view_func=config_view, methods=['GET', 'POST',])
"""

if __name__ == "__main__":
# Only for debugging while developing
	app.run(host='0.0.0.0', debug=True, port=6678)
