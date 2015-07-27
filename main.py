#!/usr/bin/python3.3

import sys 
#from lib2to3.pgen2.tokenize import bytes
sys.path.append('myIncs')

#std libs
import time
import socket


#my libs
import info
import updateDDNS
import checkNet
from TS_handler import TS
import TS_handler


#=====================================MyExit=============================#
def myExit(end):
	if end == True:
		exit()
	
	while True:
		c = input("Exit ?(y/n): ")
		
		if c == "y":
			print("Bye")
			exit()
			
		if c == "n":
			return
				
		
		print("Invalid input.")
			
	
#==================================Main================================#

while True:
	
	# ve se ha net
# 	while not checkNet.check():
# 		print("Checking for net in 5 sec's.")
# 		time.sleep(5)
	
	#	Update ddns
	#updateDDNS.update('1.2.3.6')
#  
# 	raw_msg = (7).to_bytes(1, byteorder=sys.byteorder) + (10).to_bytes(1, byteorder=sys.byteorder)
# 	print(raw_msg)
		
	print(time.time())	
	exit()
	
	ts = TS()
	
	host1 = (socket.gethostname(), 6970)
	host2 = (socket.gethostname(), 6971)
	
	sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock1.bind(host1)
	
	sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock2.bind(host2)
	
	rheader = TS_handler.Msg(mode=TS_handler.MsgToRaw, size=0, type=TS_handler.ALIVE, count=1, id=2).getRawHeader()
	sock1.sendto(rheader, (socket.gethostname(), info.port))
	
	ts.go()
	
	rawRet = sock1.recv(info.headerSize)
	msg = TS_handler.Msg(mode=TS_handler.RawToMsg, rawHeader=rawRet)
	
	print("Resp:" +':'+ str(msg.size) +':'+ str(msg.type) +':'+ str(msg.count) +':'+ str(msg.id))
	
	myExit(True)
