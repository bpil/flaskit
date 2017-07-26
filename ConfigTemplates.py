#!/usr/bin/env python

import os,sys,string,time,json,urllib2,yaml
from glob import glob

from jinja2 import Environment, FileSystemLoader
from jinja2schema import infer, to_json_schema, StringJSONSchemaDraft4Encoder

from flask import request, make_response, jsonify

ERROR_CODES = {
	'Unknown': 'Uknown error',
	'Invalid Template': '',
	'Bad Encoding': 'Request must be application/json',
	'No Action': 'Request has no Action parameter',
	'No Params': 'Action request without params argument',
	'Unknown Action': 'Type of Action is not implemented',
	'Wrong Method': 'HTTP Method not implemented'
}

def errorCode(reason='Unknown'):
	respReason = 'Unknown'
	comment = ERROR_CODES[reason]
	if reason in ERROR_CODES.keys():
		respReason = reason
		comment = ERROR_CODES[reason]
	response = make_response(jsonify(code='NOK', reason=respReason, comment=comment), 400)
	response.headers['Content-Type'] = "application/json"
	return response


class ConfigTemplate(object):

	def __init__(self, templateDir):
		self.jinjaEnv = Environment(loader=FileSystemLoader( templateDir))
		self.templateDir = templateDir

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
							response[k] = { 'source': 'input', 'type': elt['type'] }
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

	def responseTemplate(self, request, template_type):
		if request.method == 'GET':
			fileList=glob(self.templateDir + "/*.j2")
			metaList=glob(self.templateDir + ".*.yml")
			jsonSchema = ""
			for fileName in fileList:
				templateName = fileName.split('/')[-1].rstrip('.j2')
				if template_type == templateName:
					code = 'OK'
					data= {}
					dataSource = ''
					print self.templateDir + templateName + ".yml"
					if os.path.isfile(self.templateDir + "/" + templateName + ".yml"):
						f = open (self.templateDir + "/" + templateName + ".yml")
						data = yaml.load(f)
						f.close()
						dataSource = 'meta'
					else:
						source = self.jinjaEnv.loader.get_source(self.jinjaEnv, template_type + '.j2')[0]
						s = infer(source)
						data = {'params': self.parseSchema( to_json_schema(s, jsonschema_encoder=StringJSONSchemaDraft4Encoder) ) }
						dataSource = 'infer'
					response = make_response(jsonify(code=code, dataSource=dataSource, data=data), 200)
					response.headers['Content-Type'] = 'application/json'
					return response
			response = errorCode('Invalid Template')
			return response
		if request.method == 'POST':
			if not request.is_json:
				response = errorCode('Bad Encoding')
				return response
			data = request.get_json()
			if not 'action' in data.keys():
				response = errorCode('No Action')
				return response
			if data['action'] == 'render':
				if not 'params' in data.keys():
					response = errorCode('No Params')
					return response
				template = self.jinjaEnv.get_template(template_type + '.j2')
				config = template.render(data['params'])
				response = make_response(jsonify(code='OK', config=config), 200)
				return response
			response = errorCode('Unknown Action')
			return response
		response = errorCode('Wrong Method')
		return response