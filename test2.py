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

updateDDNS.update("4.4.4.4")
        