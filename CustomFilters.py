#!/usr/bin/env python

import ipaddress

def ip_plus_one( ip ):
	try:
		ipCheck = ipaddress.ip_address(ip)
	except:
		return ip
	ip_array = ip.split(".")
	last_digit = int(ip_array[3])
	last_digit += 1
	return ip_array[0] + "." + ip_array[1] + "." + ip_array[2] + "." + str(last_digit)

def lookup_dict( value, dictionary ):
	if value in dictionary.keys():
		return dictionary[value]
	return "None"