#!/usr/bin/env python

import os,sys,string,time,json,urllib2
from glob import glob

from jinja2 import Environment, FileSystemLoader
from jinja2schema import infer, to_json_schema, StringJSONSchemaDraft4Encoder

from flask import request, make_response, jsonify



class ConfigTemplate(object):

	def __init__(self, templateDir):
		self.jinjaEnv = Environment(loader=FileSystemLoader( templateDir))
		self.templateDir = templateDir
		self.ERROR_CODES = {
			'Unknown': 'Uknown error',
			'Invalid Template': '',
			'Bad Encoding': 'Request must be application/json',
			'No Action': 'Request has no Action parameter',
			'No Params': 'Action request without params argument',
			'Unknown Action': 'Type of Action is not implemented'
		}

	def parseSchema(self, schema):
		response = {}
		if 'properties' in schema.keys():
			response =  self.parseSchema(schema['properties'])
		else:
			for k in schema.keys():
				tmpList = schema[k]
				if not type(schema[k]) == 'dict':
					tmpList = [ schema[k]]
				for elt in tmpList:
					if 'properties' in elt.keys():
						response[k] = self.parseSchema(elt['properties'])
					#if 'title' in schema[k].keys():
					else:
						if 'items' in elt.keys():
							response[k]=[ self.parseSchema(elt['items']) ]
						else:
							response[k] = elt['type']
		return response

	def listTemplates(self):
		fileList=glob(self.templateDir + "/*.j2")
		tmpCode = 'OK'
		templates = []
		for fileName in fileList:
			templateName=fileName.split('/')[-1].rstrip('.j2')
			templates = templates + [templateName]
		response = make_response(jsonify(code=tmpCode, templates=templates), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	def checkTemplate(self, template_type):
		fileList=glob(self.templateDir + "/*.j2")
		response = False
		for fileName in fileList:
			templateName = fileName.split('/')[-1].rstrip('.j2')
			if template_type == templateName:
				response = True
		return response

	def errorCode(self, reason='Unknown'):
		respReason = 'Unknown'
		comment = self.ERROR_CODES[reason]
		if reason in self.ERROR_CODES.keys():
			respReason = reason
			comment = self.ERROR_CODES[reason]
		response = make_response(jsonify(code='NOK', reason=respReason, comment=comment), 400)
		response.headers['Content-Type'] = "application/json"
		return response


	def responseTemplate(self, request, template_type):
		response = make_response(jsonify(code='NOK', reason='Unknown', comment='Unkown Error'), 500)
		response.headers['Content-Type'] = "application/json"
		if request.method == 'GET':
			fileList=glob(self.templateDir + "/*.j2")
			jsonSchema = ""
			for fileName in fileList:
				templateName = fileName.split('/')[-1].rstrip('.j2')
				if template_type == templateName:
					code = 'OK'
					reason = 'OK'
					source = self.jinjaEnv.loader.get_source(self.jinjaEnv, template_type + '.j2')[0]
					s = infer(source)
	#				jsonSchema = s
					jsonSchema = self.parseSchema( to_json_schema(s, jsonschema_encoder=StringJSONSchemaDraft4Encoder) )
					response = make_response(jsonify(code=code, reason=reason, params=jsonSchema), 200)
					response.headers['Content-Type'] = 'application/json'
					return response
			response = self.errorCode('Invalid Template')
			return response
		if request.method == 'POST':
			if not request.is_json:
				response = self.errorCode('Bad Encoding')
				return response
			data = request.get_json()
			if not 'action' in data.keys():
				response = self.errorCode('No Action')
				return response
			if data['action'] == 'render':
				if not 'params' in data.keys():
					response = self.errorCode('No Params')
					return response
				template = self.jinjaEnv.get_template(template_type + '.j2')
				config = template.render(data['params'])
				response = make_response(jsonify(code='OK', config=config), 200)
				return response
			response = self.errorCode('Unknown Action')
			return response