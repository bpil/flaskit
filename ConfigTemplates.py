#!/usr/bin/env python

import os,sys,string,time,json,urllib2,yaml
from glob import glob
from inspect import getmembers, isfunction

from jinja2 import Environment, FileSystemLoader
from jinja2schema import infer, to_json_schema, StringJSONSchemaDraft4Encoder, infer_from_ast, parse, InvalidExpression

from flask import request, make_response, jsonify

import CustomFilters





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
	''' Builds a json error response.
	'''
	respReason = 'Unknown'
	comment = ERROR_CODES[reason]
	if reason in ERROR_CODES.keys():
		respReason = reason
		comment = ERROR_CODES[reason]
	response = make_response(jsonify(code='NOK', reason=respReason, comment=comment), 400)
	response.headers['Content-Type'] = "application/json"
	return response


class ConfigTemplate(object):
	''' The class handling jinja configuration files and meta files.

	Implements different json response to queries about jinja configuration files
	and their corresponding meta files.
	'''

	def __init__(self, templateDir):
		''' Simple class constructor.

		templateDir : directory where .j2 jinja template and .yml meta files are placed.
		'''
		self.jinjaEnv = Environment(loader=FileSystemLoader( templateDir))
		self.templateDir = templateDir
		for m in getmembers(CustomFilters):
			if isfunction(m[1]):
				self.jinjaEnv.filters[m[0]] = m[1]

	def errorCode(reason='Unknown'):
		return errorCode(reason)

	def parseSchema(self, schema):
		''' Converts jinja2schema dict into a more readable form.

		schema : result of jinja2schema infer operation on a jinja2 template.
		'''
		response = []
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
#							response[k] = { 'type': elt['type'], 'source': 'input' }
							response = response + [ { 'type': elt['type'], 'label': k, 'name': k } ]
		return response

	def parseYaml(self, yamlData):
		response = {}
		if type(yamlData) == 'dict':
			if 'source' in yamlData.keys():
				return True # A FINIR!!!!!!

	def listTemplates(self):
		''' Lists files with .j2 extension in self.templateDir.
		'''

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
		''' Check if template_type has a corresponding .j2 file in self.templateDir
		'''
		fileList=glob(self.templateDir + "/*.j2")
		response = False
		for fileName in fileList:
			templateName = fileName.split('/')[-1].rstrip('.j2')
			if template_type == templateName:
				response = True
		return response

	def responseTemplate(self, request, template_type):
		''' Builds a json response to a query of <template_type>

		request : HTTP request. Valid requests are GET and POST
		GET request : returns the content of the meta file corresponding to the template, or
		the inferred parameters json (from jinja2schema) if no meta file exists
		POST request : returns the rendered template file with the parameter given in POST data

		template_type : the name of the template to infer or render
		'''
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
					if os.path.isfile(self.templateDir + "/" + templateName + ".yml"):
						f = open (self.templateDir + "/" + templateName + ".yml")
						yamlData = yaml.load(f)
						f.close()
						yamlParams = yamlData['params']
						data = yamlParams
						dataSource = 'meta'
					else:
						s = {}
						source = parse(self.jinjaEnv.loader.get_source(self.jinjaEnv, template_type + '.j2')[0], self.jinjaEnv)
#						source = parse(self.jinjaEnv.get_template(template_type + '.j2'), self.jinjaEnv)
						try:
							s = infer_from_ast(source)
						except InvalidExpression:
							pass
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

	def getTemplate(self, template_type):
		fileList=glob(self.templateDir + "/*.j2")
		metaList=glob(self.templateDir + ".*.yml")
		jsonSchema = ""
		for fileName in fileList:
			templateName = fileName.split('/')[-1].rstrip('.j2')
			if template_type == templateName:
				code = 'OK'
				data= {}
				dataSource = ''
				if os.path.isfile(self.templateDir + "/" + templateName + ".yml"):
					f = open (self.templateDir + "/" + templateName + ".yml")
					yamlData = yaml.load(f)
					f.close()
					yamlParams = yamlData['params']
					data = yamlParams
					dataSource = 'meta'
				else:
					s = {}
					source = parse(self.jinjaEnv.loader.get_source(self.jinjaEnv, template_type + '.j2')[0], self.jinjaEnv)
#						source = parse(self.jinjaEnv.get_template(template_type + '.j2'), self.jinjaEnv)
					try:
						s = infer_from_ast(source)
					except InvalidExpression:
						pass
					data = {'params': self.parseSchema( to_json_schema(s, jsonschema_encoder=StringJSONSchemaDraft4Encoder) ) }
					dataSource = 'infer'
				response = make_response(jsonify(code=code, dataSource=dataSource, data=data), 200)
				response.headers['Content-Type'] = 'application/json'
				return response
		response = errorCode('Invalid Template')
		return response

	def postTemplate(self, request, template_type):
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