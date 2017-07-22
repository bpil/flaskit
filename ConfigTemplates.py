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

	def parseSchema(self, schema):
	#	print schema
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
							response[k]=self.parseSchema(elt['items'])
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

	def responseTemplate(self, request, template_type):
		response = make_response(jsonify(code='NOK', reason='Unknown', comment='Unkown Error'), 500)
		response.headers['Content-Type'] = "application/json"
		if request.method == 'GET':
			fileList=glob(self.templateDir + "/*.j2")
			code = 'NOK'
			reason = 'Invalid template'
			jsonSchema = ""
			for fileName in fileList:
				templateName = fileName.split('/')[-1].rstrip('.j2')
				if template_type == templateName:
					code = 'OK'
					reason = 'OK'
					source = self.jinjaEnv.loader.get_source(self.jinjaEnv, template_type + '.j2')[0]
					s = infer(source)
	#				jsonSchema = s
					print to_json_schema(s, jsonschema_encoder=StringJSONSchemaDraft4Encoder)
					jsonSchema = self.parseSchema( to_json_schema(s, jsonschema_encoder=StringJSONSchemaDraft4Encoder) )
					print jsonSchema
			response = make_response(jsonify(code=code, reason=reason, params=jsonSchema), 200)
			response.headers['Content-Type'] = 'application/json'
			return response
		if request.method == 'POST':
			if not request.is_json:
				response = make_response(jsonify(code='NOK', template=template_type, reason='Bad format', comment='Request must be application/json'), 400)
				response.headers['Content-Type'] = 'application/json'
				return response
			data = request.get_json()
			template = self.jinjaEnv.get_template(template_type + '.j2')
			config = template.render(data)
			response = make_response(jsonify(code='OK', config=config), 200)
			return response