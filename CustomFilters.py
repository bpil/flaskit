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

DICTIONARIES = {
	'example_dict': {
		'key1': 'value1',
		'key2': 'value2'
	},
	'l2l_encap_mtu': {
		'ethernet-ccc': '1500',
		'vlan-ccc': '1508'
	}
}

def lookup_dict( value, table_name ):
	if table_name in DICTIONARIES.keys():
		lookup_table = DICTIONARIES[table_name]
		if value in lookup_table.keys():
			return lookup_table[value]
	return "None"

def isis_id( ip ):
	try:
		ipCheck = ipaddress.ip_address(ip)
	except:
		return "6666.6666.6666"
	octets = ip.split(".")
	alloctets = ""
	for o in octets:
		alloctets += "%03d" % (int(o),)
	print type(alloctets)
	print alloctets
	return alloctets[0:4] + "." + alloctets[4:8] + "." + alloctets[8:12]
