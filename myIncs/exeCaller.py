#!/usr/bin/python3.3
'''
Created on 29 Dec 2013

@author: alexandre
'''

import os
import time
import socket
import array
import subprocess
import platform
import info
import signal

class Process:
    def __init__(self, args):
            self._path = args
            if (platform.system() == "Linux"):
                self._proc = subprocess.Popen(args, shell=True, universal_newlines=True)
            elif (platform.system() == "Windows"):
                #self._proc = subprocess.Popen("sl_ts3server_win32.exe", shell=True, universal_newlines=True)
                os.system('start ' + args)
    #end __init__(...)
    
    def start(self):
        pass
    #end start(...)
            
    def kill(self):
        if (platform.system() == "Linux"):
            self._proc.kill()
        elif (platform.system() == "Windows"):
            os.system('taskkill /f /im ts3server_win32.exe')
        self._proc.wait()
    #end kill(...)
    
#end class Process
