#!/usr/bin/python3.3

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> NAO MUDEM ESTA MERDA !!! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# a não ser que saibam o que estão a fazer

# Conta no-ip.com
user = 'alexbig2'
password = 'unreal1234'
noipURL = 'dynupdate.no-ip.com'

# Address do TS
address = 'soulcasa.no-ip.biz'

# Path to ts-server
import platform
if (platform.system() == "Linux"):
    tsPath = "./testexe.sh"
elif (platform.system() == "Windows"):
    tsPath = "\"teamspeak3-server_win32\ts3server_win32.exe\""
    
#
#    TS Handler
#

# TS Handler port
port = 26969

# tempo entre ticks, para nao ser tao pesado
tickPeriod = 0.100

# DTSSP
hSizeBytes = 1 #byte(s)
hTypeBytes = 1
hCountBytes = 4
hIdBytes = 4

headerSize = hSizeBytes + hTypeBytes + hCountBytes + hIdBytes

timeout = 3.5 # sec(s)
retryTime = 2.5 
shortTimeout = 2.5
shortRetryTime = 1.5

# connect
connTimeout = 1.5 # sec(s)
connShortTimeout = 0.250
connRetrys = 4 # quantidy

debug0 = 0
