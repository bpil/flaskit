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
	comment = ERROR_CODES['Unknown']
	if reason in ERROR_CODES.keys():
		respReason = reason
		comment = ERROR_CODES[reason]
	return { 'code': 400, 'data': {'reason': respReason, 'comment': comment} }


class ConfigTemplate(object):
	''' The class handling jinja configuration files and meta files.

	Implements different json response to queries about jinja configuration files
	and their corresponding meta files.
	Response are REST-like Dict in the form :
	{
		'code': <Integer: HTML return code>,
		'data': <Dict: JSON data>
	}
	<JSON data> depends on type of request / response.
	For Error Code response :
	data:
	{
		'code': <String: Error Code>,
		'comment': <String: Error Description>
	}
	For Template GET request :
	data : 
	{
		'inputs': <List of Dicts: Input descriptors>
	}

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
		self.templateList = {}
		for templateFile in glob(self.templateDir + "/*.j2"):
			templateName = templateFile.split('/')[-1].rstrip('.j2')
			data = {}
#			templateList = templateList + [ templateName ]
			if not os.path.isfile(self.templateDir + "/" + templateName + ".yml"):
				source = parse(self.jinjaEnv.loader.get_source(self.jinjaEnv, templateName + '.j2')[0], self.jinjaEnv)
				s = infer_from_ast(source)
				data = {'inputs': to_json_schema(s, jsonschema_encoder=StringJSONSchemaDraft4Encoder) }
				f = open(self.templateDir + "/" + templateName + ".yml", 'w')
				f.write(yaml.dump(data))
				f.close()
			else:
				f = open(self.templateDir + "/" + templateName + ".yml", 'r')
				data = yaml.load(f)
				f.close()
			self.templateList[templateName] = data



	def errorCode(reason='Unknown'):
		return errorCode(reason)


	def listTemplates(self):
		''' Lists files with .j2 extension in self.templateDir.
		'''

		response = { 'code': 200, 'data': { 'templates': self.templateList.keys() } }
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


	def getTemplate(self, template_type):
		if template_type in self.templateList.keys():
			return { 'code': 200, 'data': self.templateList[template_type]['inputs'] }
		return errorCode('Invalid Template')


	def postTemplate(self, request, template_type):
		if not request.is_json:
			return errorCode('Bad Encoding')
		print request.get_json()
		data = json.dumps(request.get_json())
		data = request.get_json()
		template = self.jinjaEnv.get_template(template_type + '.j2')
		config = template.render(data)
		print type(config)
		return { 'code': 200, 'data': {'config': config }}