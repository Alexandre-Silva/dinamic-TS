import urllib3
import socket
import urllib3
import info
import xml.etree.ElementTree as ET

def getExternalIp():       
    try:
        # Pede ao server o ip externo
        conn = urllib3.connection_from_url('http://' 
                                           +socket.gethostbyname('checkip.dyndns.org'),
                                           timeout=2.0)
        r = conn.request('GET', '/')
        
        # a partir do HTML recebi faz parse e e retira a string com o ip
        root = ET.fromstring(r.data)
        externalIP = root.find('body').text.replace("Current IP Address: ", "")
        
        print("Your External IP Address is: ",externalIP)
        return externalIP
   
    except Exception as e:
        print(e.args)
        print()
        print("ERROR: Couldn't get the External IP")
        print()
        raise
             
#end _setExternalIp(...)

def tryGoogle():
    lstCNIPs = []
    lstCNIPs.append('http://74.125.228.100')
    lstCNIPs.append('http://173.194.41.215')
    lstCNIPs.append('http://173.194.41.216')
    lstCNIPs.append('http://173.194.41.223') 
    lstCNIPs.append('http://' + socket.gethostbyname('www.google.com'))
    lstCNIPs.append('http://' + socket.gethostbyname('www.google.pt'))
   

    for ip in lstCNIPs:
        try:
            print("--Trying: " + ip)
            conn = urllib3.connection_from_url(ip, timeout=1000.0)
            conn.request('GET', '/')
            return True
        #except urllib3.URLError as err: pass
        except :
            pass
        
    return False

def check():
    print("Checking for net")
    
    if tryGoogle():
        print("WWW is up.")
        return True
    else:
        print("ERROR: Vai pagar a net o caloteiro.")
        return False




# import urllib2
# 
# def internet_on():
#     try:
#         response=urllib2.urlopen('http://74.125.228.100',timeout=1)
#         return True
#     except urllib2.URLError as err: pass
#     return False
# 
# 
# # V2
# # Python 2.7
# 
# import urllib
# 
# url = 'http://www.boursorama.com/includes/cours/last_transactions.phtml?symbole=1xEURUS'
# sock = urllib.urlopen(url)
# content = sock.read() 
# sock.close()
# 
# print content



# try:
#     #timeout = urllib3.util.timeout(connect=2.0, read=7.0)
#     #pool = urllib3.HTTPConnectionPool('http://74.125.228.100', maxsize=1, timeout=1.0)
#     #pool.request("GET", 'http://74.125.228.100', fields, headers)
#     #pool.request(method, url, fields, headers)
#     #con = urllib3.connection_from_url('http://74.125.228.100', timeout=1.0)
#     #r = pool.urllib3.request('http://74.125.228.100', timeout=1.0)
# 
#     print("Net up")
# except: 
#     print("No net")

#urllib3.urlopen('http://74.125.228.100')

    
    
