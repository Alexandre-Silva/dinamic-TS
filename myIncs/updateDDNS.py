#!/usr/bin/python3.3

'''
Created on 18 Dec 2013

@author: alexandre
'''

import socket
import urllib3

import info


# Debug
#myip = '1.2.3.6'

def update(ip="noIP"):

	
	# Login trough url
	header = urllib3.util.make_headers(basic_auth=info.user
									   +':'
									   +info.password)
	
	# url parameters && check if ip is legal
	try:
		socket.inet_aton(ip)
		
		# legal
		field = {'hostname': info.address, 'myip': ip}
	except socket.error:
		# Not legal
		field = {'hostname': info.address}
	
	try:
	# Cria obj para ligaçao ao site do ddns
		conn = urllib3.connection_from_url('http://' 
										   +socket.gethostbyname(info.noipURL))
	
	# Envia o pedido para actualizar o ip
		conn.request('GET', '/nic/update',
					 fields = field,
					 headers = header)
	except Exception as e:
		print("ERROR: Couldn't update ddns, error follows:\n", e)
