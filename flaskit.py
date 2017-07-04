#!/usr/bin/env python

import os,sys,string,time,json,urllib2
from glob import glob
from pymongo import MongoClient

from flask import Flask, request, make_response, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello World!'


@app.route('/templatize/<template_type>', methods=['GET', 'POST'])
def templatize(template_type):
	if request.method == 'GET':
		response = make_response(jsonify(code='OK', template=template_type), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	if request.method == 'POST':
		if not request.is_json:
			response = make_response(jsonify(code='NOK', template=template_type, reason='Bad format', comment='Request must be application/json'), 400)
			response.headers['Content-Type'] = 'application/json'
			return response
		data = request.get_json()
		return "OK"