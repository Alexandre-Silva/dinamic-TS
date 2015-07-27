'''
Created on 18 Dec 2013

@author: alexandre
'''

#TODO: tirar o info.debug0

import info
import socket
import time
import sys
from symbol import except_clause
import checkNet
import traceback
import updateDDNS
import exeCaller

# init modes
RawToMsg = 1
MsgToRaw = 2

# Message types
#    header only
ACK = 0
KEEPALIVE = 1
REQPEERS = 2
CLOSEPEER = 3
REGISTER = 4
#     heade + body
SENDPEERS = 5
NEWTSS = 6

MsgTypeStr = []
MsgTypeStr.insert(ACK, "ACK")
MsgTypeStr.insert(KEEPALIVE, "KEEPALIVE")
MsgTypeStr.insert(REQPEERS, "REQPEERS")
MsgTypeStr.insert(CLOSEPEER, "CLOSEPEER")
MsgTypeStr.insert(REGISTER, "REGISTER")
MsgTypeStr.insert(SENDPEERS, "SENDPEERS")

class Msg:
    def __init__(self, mode, addr=None, peerID=None,
                 rawHeader=None, size=None, msgType=None, count=None, msgID=None, body=None):
        
        self.addr=addr
        
        if (mode == RawToMsg):
            self._parseRawHeader(rawHeader)
            self.body = body
     
        elif (mode == MsgToRaw):
            self.size = 0
            self.type = msgType
            self.count = count
            self.id = msgID
            self.body = body
            
            if (body != None):
                self.size = len(self.body) # 1 char == 1 byte
    #end __init__(...)
                                
    def getRawHeader(self):
        return self._buildRawHeader()
    
    def setBodyFromRaw(self, rawBody):
        self._parseRawBody(rawBody)
    
    def getRawMsg(self):
        return self._buildRawHeader() + self._buildRawBody()
        #TODO: meter o body na msg
    
    def toStrf(self):
        #returns a str describing the msg
        ret  = "MSG"
        ret += "\n-Size: " + str(self.size)
        ret += "\n-Type: " + MsgTypeStr[self.type]
        ret += "\n-Count: " + str(self.count)
        ret += "\n-MsgID: " + str(self.id)
        
        if (self.body != None):
            ret += "\n-Body: " + self.body
        
        return ret 
    #end toStrf(...)
    
    
    def _parseRawHeader(self, rawHeader):
        i = 0
        
        self.size = int.from_bytes(rawHeader[i : i + info.hSizeBytes], sys.byteorder)
        i = i + info.hSizeBytes
        
        self.type = int.from_bytes(rawHeader[i : i + info.hTypeBytes], sys.byteorder)
        i = i + info.hTypeBytes
        
        self.count = int.from_bytes(rawHeader[i : i + info.hCountBytes], sys.byteorder)
        i = i + info.hCountBytes
        
        self.id = int.from_bytes(rawHeader[i : i + info.hIdBytes], sys.byteorder)
        i = i + info.hIdBytes
    #end _parseRawHeader(...)
    
    def _parseRawBody(self, rawBody):
        self.body = rawBody.decode(encoding='utf_8', errors='strict')
    
    
    def _buildRawHeader(self):
        
        rawHeader  = self.size.to_bytes(info.hSizeBytes, byteorder=sys.byteorder)
        rawHeader += self.type.to_bytes(info.hTypeBytes, byteorder=sys.byteorder)
        rawHeader += self.count.to_bytes(info.hCountBytes, byteorder=sys.byteorder)
        rawHeader += self.id.to_bytes(info.hIdBytes, byteorder=sys.byteorder)
        
        return rawHeader
    #end _buildRawHeader(...)
    
    def _buildRawBody(self):
        if (self.body == None):
            return b''
        else:
            return self.body.encode(encoding='utf_8', errors='strict')
    #end _buildRawBody(...)

        


class Pending:
    def __init__(self):
        self.lst = []
    
    def _add(self, msg):
        self._lstPending.append(msg)
       
        
    def _rm(self, addr, mID):
        #Return True if sucessfully, False otherwise
        for msg in self.lst:
            if (addr == msg.addr and id == msg.mID):
                self.lst.remove(msg)
                return True
        return False
    
    
    def _find(self, addr, mID):
        #Return the msg if sucessfully, False otherwise
        for msg in self.lst:
            if (addr == msg.addr and id == msg.mID):
                return msg
        return False


#
#        PEER
#
# Peer Exceptions
class NoData(Exception):
    def __init__(self):
        return

class ConnectionLost(Exception):
    def __init__(self):
        return

# Peer states

ON=0
NEEDKA=1
KASENT=2
CONNECTIONLOST=3
MARKED=4
CLOSED=5
CONNECTIONTIMEDOUT = 6
PeerStatusStr = []
PeerStatusStr.insert(ON, "ON")
PeerStatusStr.insert(NEEDKA, "NEEDKA")
PeerStatusStr.insert(KASENT, "KASENT")
PeerStatusStr.insert(CONNECTIONLOST, "CONNECTIONLOST")
PeerStatusStr.insert(MARKED, "MARKED")
PeerStatusStr.insert(CLOSED, "CLOSED")
PeerStatusStr.insert(CONNECTIONTIMEDOUT, "CONNECTIONTIMEDOUT")

class Peer:
    def __init__(self, connection, addr, shortTime=False):
        
        self._sock = connection
        self._sock.settimeout(0)
        
        self.addr = addr#addr # ip
        self.hostname = None
        self.status = ON
        self.isTss = False # this value is posterioly setted
        self.msgID = 0
        self._shortTime = shortTime
        
        self._resetTimeout()

    def sendMsg(self, msgType, tsCount=0, data=None):
        # Sends a message to this peer
        # returns True if the message was sucessfully sent
        # returns False otherwise
        if(self.status == (CONNECTIONLOST or MARKED or CLOSED)):
            return False
        
        msg = Msg(MsgToRaw, msgType=msgType, count=tsCount, msgID=self.msgID, body=data)
        self.msgID += 1
        try:
            self._sock.send(msg.getRawMsg())
            return True
        except BrokenPipeError:
            self.status = CONNECTIONLOST
            return False
        except ConnectionAbortedError:
            self.status = CONNECTIONLOST
            return False
        except Exception as e:
            print()
            print("ERROR: connection lost to: "+ self.addr)
            print(e.args)
            self.status = CONNECTIONLOST
            return False
            
        
        
    def recvMsg(self):
        # returns a new msg from this peer, and reset the retry and timout timers if msg received
        # returns None, if no new Msg was received
        # raises ConnectionLost if tcp socket lost connection
        if(self.status == (CONNECTIONLOST or CLOSED)):
            return None
        
        try:
            rawHeader = self._sock.recv(info.headerSize)
            if (rawHeader == b''):
                self.status = CONNECTIONLOST
                raise ConnectionLost()
            else:
                self._resetTimeout()
                self.status = ON
                msg = Msg(RawToMsg, rawHeader=rawHeader)
                if (msg.size == 0):
                    return msg
                else:
                    msg.setBodyFromRaw(self._sock.recv(msg.size))
                    return msg
                
        except BlockingIOError:
            return None
        except socket.timeout:
            return None
        except OSError as e:
            print("ERROR: unknow error: " + str(e.args) + "\n-At Peer.recvMsg()")
            return None
        
    def checkStatus(self, t=None):
        # returns the status of the Peer
        # closes the peer if it is set to be be closed
        # also closes the peer is it has timed out 
        # or teh connection has been lost
        
        if (t == None):
            t = time.time()
    
        if (self.status == CONNECTIONLOST):
            print(self._getStatusStrf())
            self.closePeer()
            return self.status
        
        if (self.status == MARKED):
            print(self._getStatusStrf())
            self.closePeer()
            return self.status
        
        if (t < self.retryTime):
            return self.status
        
        elif (t <  self.timeout and self.status == ON):
            self.status = NEEDKA
            #print(self._getStatusStrf())
            return self.status
        
        elif (t <  self.timeout and self.status == NEEDKA):
            print("Warning KA not sent")
            return self.status
        
        elif (t <  self.timeout and self.status == KASENT):
            return self.status
        
        elif (t >=  self.timeout):
            self.status = CONNECTIONTIMEDOUT
            print(self._getStatusStrf())
            self.closePeer()
            return self.status
        
        print("ERROR: unnexpected peer status:" + self.status)
        for tline in traceback.format_stack():
            print( tline.strip())
            
        return self.status
    #end checkStatus(...)
    
    def setIsTSS(self, st):
        # sets the retry/timeout timer to the short or normal time
        # st bool
        self._shortTime = st
        self.isTss = st
        self._resetTimeout()
        
    def sendKA(self, count=0):
        self.sendMsg(KEEPALIVE, count)
        self.status = KASENT
        #print(self._getStatusStrf())
        
    def markToClose(self):
        self.status = MARKED
        
    def closePeer(self):
        self.status = CLOSED
        self._sock.close()
        
    def getAddrf(self):
        return str(self.addr[info.debug0]) +':'+ str(self.hostname)

    def _getStatusStrf(self):
        if(self.isTss == False):
            me = "Peer"
        else:
            me = "Tss"
        return "Connection to "+me+": " + str(self.addr[info.debug0]) + "\n    status: " + PeerStatusStr[self.status]
    #end _getStatusStrf(...)
        
    def _resetTimeout(self):
        if (self._shortTime == True):
            self.retryTime = time.time()
            self.timeout = self.retryTime + info.shortTimeout
            self.retryTime += info.shortRetryTime
        else:        
            self.retryTime = time.time()
            self.timeout = self.retryTime + info.timeout
            self.retryTime += info.retryTime
                    
#                
#    LISTENER
#
# Listener exceptions
class NoNewPeer(Exception):
    def __init__(self):
        return

class Listener:
    # TODO comentar isto
    def __init__(self, port=info.port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(('', port))
        self._sock.listen(5)
        self._sock.settimeout(0)
        
        self._port = port #TODO: dev only
        
    def checkConnections(self):
        # returns a list of new Peers
        # returns None if no new Peer
        ret = []
        while True:
            try:
                c, addr = self._sock.accept()
                ret.append(Peer(c, addr))
            except socket.timeout:
                break
            except BlockingIOError:
                break
        return ret
            
    def close(self):
        self._sock.close()
                
                
class NoNet(Exception):
    def __init__(self):
        print("Lost connection to the WWW")
        return
                

# States
STARTINGUP=0
ONLINE=1
NEWCOUNT=2
SHUTINGDOWN=3
TSSDOWN=4


class TS:
    #TODO comentar isto
    def __init__(self):
        self.externalIp = checkNet.getExternalIp() # TODO: isto tb
        
        self._listener = None#TODO: meter isto como deve de ser Listener()
        
        #init various variables
        #self.pending = Pending()
        self._count = 0
        self._status = STARTINGUP
        self._tssPeers = []
        self._tss = None
        
        #peer related stuff
        self._peers = []
    #end __init__(...)
    
    def go(self, ip=info.address, port=info.port):
        ip = socket.gethostbyname(ip)
        self._noNetTimeout = time.time() + info.timeout
        
        if ((ip == '1.1.1.1') or (ip == self.externalIp)):
            self._tss = None
            print("TS server is not up")
        else:
            print("TS server is up at : "+ ip)
            self._tss = self._connectToPeer(ip, port, info.connTimeout, info.connRetrys)
        
        while True:
            #ts server not up
            if (self._tss == None):
                ret = self._serverTick()
                
            #ts server is up
            else:
                self._tss.setIsTSS(True)
                ret = self._clientTick()
    #end go(...):
    
    
    def terminate(self):
        if (self._listener != None):
            self._listener.close()
            
        # if it ISEN'T the server
        if (self._tss != None):
            try:
                self._tss.sendMsg(CLOSEPEER)
                self._tss.closePeer()
            except Exception as e:
                print(e.args)
        
        # if it IS the server
        else:
            self._svProcess.kill()
            
            # if there are no peers connected
            if (self._peers == []):
                updateDDNS.update('1.1.1.1')
                print("TS server is beeing closed on local machine, and there are no peers connected.")
                print("Setting ddns ip to 1.1.1.1")
        
            else:
                for p in self._peers:
                    try:
                        p.sendMsg(CLOSEPEER)
                        p.closePeer()
                    except Exception as e:
                        print(e.args)
                        
        print("TS_handler has been terminated")
        return
    #end terminate(...)
    
    def _buildPeerLst(self):
        # return a str of ip:hostname pairs (ex. "1.2.3.4:user1;6.7.8.9:user2;10.11.12.13:user3")
        # returns None if there are no Peers
        
        ret = ''
        
        # if it is the tss 
        if (self._tss == None): 
            for p in self._peers:
                if (ret != ''):
                    ret += ';'
                ret += str(p.addr[info.debug0]) + ":" + str(p.hostname)
                
        # if it isen't the tss
        else:
            for ip in self._tssPeers:
                if (ret != ''):
                    ret += ';'
                ret += ip
        if (ret == ''):
            return None
        else:
            return ret
    #end _buildPeerLst(...)

    def _parsePeerLst(self, rawIPLst):
        ret = rawIPLst.split(sep=';')
        
        i=0
        for i in range(0,len(ret)):
            ret[i] = ret[i].split(sep=':')
            if (info.debug0 == 1):
                ret[i] = [int(ret[i][0]), ret[i][1]]
        return ret
    #end _parsePeerLst(...)
    
    def _checkListener(self):
        #acepts and adds new peers to ts._lstPeers[]
        if (self._listener == None): #TODO: tirar isto , so pa development
            return 
        lstP = self._listener.checkConnections()
        if (lstP != []):
            for p in lstP:
                print("Peer: " + str(p.addr) + " has connected\n    status: ON")
            self._peers.extend(lstP)
            self._count += 1
            if (self._count == 255):
                self._count = 1
            self._status = NEWCOUNT
    #end _checkListener(...)

    def _assertNewTss(self):
        # returns the lowest ip address from all active Peers (connecterd or not)
        # if it is the tss and should there be no other active peers it returns None 
        # if it isen't the tss and should there be no other active peers it returns his won externalIP
        
        # if it is the tss
        if (self._tss == None):
            if (self._peers == []):
                return None
            
            newTss = self._peers[0].addr[info.debug0]
            for p in self._peers:
                if (newTss > p.addr[info.debug0]):
                    newTss = p.addr[info.debug0]
            return newTss
        
        # if it isen't the tss
        else:
            if (self._tssPeers == []):
                return self.externalIp
            
            newTss = self._tssPeers[0]
            for p in self._tssPeers:
                if (newTss[0] > p[0]):
                    newTss = p
            return newTss
    #end _assertNewTss(...)
        
    def _connectToPeer(self, ip, port=info.port, timeout=info.connShortTimeout, retrys=1):
        # atempts to connect to a Listener in (ip, port)
        # returns a Peer if sucessfull 
        # returns None if unsucessfull
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((socket.gethostname(), 0))
        sock.settimeout(timeout)
        for i in range(0, retrys):
            try:
                print("Trying to conect to: " + str(ip) + ":" + str(port))
                sock.connect((ip, port))
                return Peer(sock, (ip, port))
            
            except socket.timeout:
                print("Connection attempt failed: socket.timeout")
                time.sleep(timeout)
                continue
            
            except ConnectionRefusedError:
                print("Connection attempt failed: ConnectionRefusedError")
                time.sleep(timeout)
                continue
            
            except ConnectionAbortedError:
                print("Connection attempt failed: ConnectionAbortedError")
                time.sleep(timeout)
                continue

            except PermissionError:
                print("ERROR: Insufficient permission to connect to Listener at: " + str((ip, port)))
                break
        return None
    # end _connect(..)    
                   
    def _checkPeers(self):
        # checks peers ofr timeouts and retrys times, to send keep alive msg's
        # removing those who have timed out, are closeed or marked to be removed
        t = time.time()
        newCount=False
        for p in self._peers:
            pStatus = p.checkStatus(t)
            
            if (pStatus == ON):
                pass
            
            elif (pStatus == NEEDKA):
                p.sendKA(self._count)
                pass
            
            elif (pStatus == KASENT):
                pass
            
            elif (pStatus == CLOSED):
                self._peers.remove(p)
                newCount = True
                pass
        #end for p in self._peers:
        
        if (newCount == True):
            self._count += 1
            if (self._count == 255):
                self._count = 1
            self._status = NEWCOUNT
    #end _checkPeers(...)
    
    def _checkTSS(self):
        # checs isTss ofr timeouts and retrys times, to send keep alive msg's
        if (self._tss == None):
            self._status = TSSDOWN
            return
        
        pStatus = self._tss.checkStatus()
        if (pStatus == ON):
            pass
        
        elif (pStatus == NEEDKA):
            self._tss.sendKA(self._count)
            pass
        
        elif (pStatus == KASENT):
            pass
        
        elif (pStatus == CLOSED):
            self._status = TSSDOWN
            self._tss = None
            pass
    #end _checkTSS(...)

    def _recvAllMsgs(self):
        # checks all peers and isTss for new msg's
        # returns a list of (msg, peer) if new msgs are received by peers
        # returns an empty list if there are no new Msgs
        ret = []
        while self._tss != None:
            try:
                msg = self._tss.recvMsg()
                if (msg == None):
                    break
                else:
                    ret.append((msg, self._tss))
                    continue
                    
            except ConnectionLost:
                self._status = TSSDOWN
                break
            
        for p in self._peers:
            while True:
                try:
                    msg = p.recvMsg()
                    if (msg == None):
                        break
                    else:
                        ret.append((msg, p))
                        continue
                        
                except ConnectionLost:
                    break
                    
        return ret
    #end _recvAllMsgs(...)
           
    def _serverTick(self):
        # main cycle for server
        while True:
            #new connections
            self._checkListener()
            
            #check peers status
            self._checkPeers()
                   
            #new msgs
            lstMsg = self._recvAllMsgs()
            for msg, p in lstMsg:
                if (msg.type == ACK):
                    continue                
                
                if (msg.type == KEEPALIVE):
                    if(not p.sendMsg(ACK, self._count)):
                        pass
                    continue
                 
                if (msg.type == REGISTER):
                    msgBody = msg.body
                    msgBody = msgBody.split(sep=';') #TODO: meter isto a dar com o CHTSS
                    p.hostname = msgBody[0]
                    if (msgBody[1] == 'True'):
                        p.sendMsg(ACK, self._count)
                    else:
                        print("ERROR: at register")
                    
                    if (info.debug0 == 1):#dev TODO: dev only
                        p.addr = (p.addr[0], int(msgBody[2]))
                        self._status = NEWCOUNT
                        print("New peer: " + p.getAddrf())
                    
                    continue   
                    
                if (msg.type == CLOSEPEER):
                    p.markToClose()
                    continue
                
                if (msg.type == REQPEERS):
                    if(not p.sendMsg(SENDPEERS, self._count, self._buildPeerLst())):
                        pass
                    continue
                
                print("WARNING: An unknown/currupted msg was received from : " + str(p.addr[info.debug0]))
                print(msg.toStrf())
                
            if (self._status == ONLINE):
                if (self._peers == [] and self._noNetTimeout < time.time()):
                    if (checkNet.check() == True):
                        self._noNetTimeout = time.time() + info.timeout
                    else:
                        self.terminate()
                        raise NoNet()
                
            elif (self._status == NEWCOUNT):
                peerLst = self._buildPeerLst()
                if (peerLst == None):
                    print("No connected Peers")
                else:
                    print("Connected peers: ")
                    for peer in self._peers:
                        print("-"+peer.getAddrf())
                    for p in self._peers:
                        if(not p.sendMsg(SENDPEERS , self._count, peerLst)):
                            pass
                self._status = ONLINE
                
            elif (self._status == STARTINGUP):
                self._count = 1
                self._status = ONLINE
                self._noNetTimeout = time.time() + info.timeout
                self._svProcess = exeCaller.Process(info.tsPath)
                updateDDNS.update()
                print("TS server started on local machine")
                
            time.sleep(info.tickPeriod) 
        #end while True                    
    #end _serverTick(...)
    
    def _clientTick(self):
        # main cycle for server state
        while True:
            #new connections
            self._checkListener()
            
            #check peers status
            self._checkPeers()
            self._checkTSS()
            
            #new msgs from Peers nad isTss
            lstMsg = self._recvAllMsgs()
            for msg, p in lstMsg:
                if (p == self._tss):
                    self._count = msg.count
                
                if (msg.type == ACK):   
                    continue
                
                if (msg.type == KEEPALIVE):
                    p.sendMsg(ACK, self._count)
                    continue
                
                if (msg.type == SENDPEERS and p == self._tss):
                    self._tssPeers = self._parsePeerLst(msg.body) # isto é o k deve tar normalmente
                    print("Received new Peer list from Tss:")
                    for peer in self._tssPeers:
                        print("-"+str(peer[0]) + ":" + str(peer[1]))
                    continue
                    
                if (msg.type == CLOSEPEER):
                    p.markToClose()
                    continue
                
                print("WARNING: An unknown/currupted msg was received from : " + p.getAddrf())
                
                
            # client operations
            if (self._status == ONLINE):
                pass
                
            elif (self._status == TSSDOWN):
                #checks if connections lost is due to loss of net
                if (checkNet.check() == False):
                    self.terminate()
                    raise NoNet()
    
                print("TS Server is down")
                newTss = self._assertNewTss()
                if (newTss[0] == self.externalIp):
#                     if (self._tss != None):
#                         self._tss.setIsTSS(False)
#                         self._peers.append(self._tss)
#                         self._checkPeers() # caution, if the tss status is CLOSED this funtions changes sel._status to NEWCOUNT
                    self._tss = None
                    self._status = STARTINGUP # that is why this line is extremely important
                    self._tssPeers = []
                    return 
                
                else:
                    print(self._tssPeers)
                    print("newTss: ")
                    print(newTss)
                    self._tssPeers.remove(newTss)
                    self._tss = self._connectToPeer(socket.gethostname(), newTss[0], info.connTimeout, info.connRetrys)
                    self._status = STARTINGUP
                
            elif (self._status == STARTINGUP):
                print("Current TS Server at: " + self._tss.getAddrf())
                if (not info.debug0 ):
                    self._tss.sendMsg(REGISTER, self._count, socket.gethostname() + ';' + 'True')
                else:
                    self._tss.sendMsg(REGISTER, self._count, socket.gethostname() + ';' + 'True' + ';' +str(self._listener._port))#TODO:dev only
                
                self._status = ONLINE
            
            time.sleep(info.tickPeriod)      
    #end _clientTick(...)
    
    
    