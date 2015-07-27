#!/usr/bin/python3.3

'''
Created on 29 Dec 2013

@author: alexandre
'''
import sys 
#from lib2to3.pgen2.tokenize import bytes
sys.path.append('myIncs')

#std libs
import time
import socket
import array
import subprocess
import urllib3
import os

#my libs
import info
import updateDDNS
import checkNet
from TS_handler import TS
import TS_handler
import exeCaller

#p = exeCaller.Process(None)
os.system('start /D teamspeak3-server_win32 ts3server_win32.exe')

time.sleep(5)
print("Now killing the tsSV")

#p.kill()
os.system('taskkill /f /im ts3server_win32.exe')
