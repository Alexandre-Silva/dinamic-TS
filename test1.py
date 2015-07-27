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

lb = socket.gethostname()

try:
    ts = TS()
    ts._listener = TS_handler.Listener()
#    ts.externalIp = 6970
#    ts._status = TS_handler.ONLINE
    ts.go()
    
except KeyboardInterrupt as e:
    print()
    try:
        ts.terminate()
        print("Terminated")
    except Exception as e:
        print(str(e.with_traceback(None).args))
        






