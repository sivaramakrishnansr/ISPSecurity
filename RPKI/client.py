import socket, ssl, pprint
import time

start=time.time()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ssl_sock = ssl.wrap_socket(s,
                           ca_certs="/proj/SENSS/certificates/server-chain.crt",
                           cert_reqs=ssl.CERT_REQUIRED)

ssl_sock.connect(('192.168.3.178', 10023))
end=time.time()
print "Time to connect via SSL and RPKI",end-start

#Different types of Request
#1 - Observation On a Match Type
#2 - Add Flow - On a Match Type 
#3 - Remove Flow - On Match Type
#4 - Get Route - No data
#5 - Promote Route - No data
#6 - Demote Route - No data

a={"LosAngeles":2}
send_array={}
send_array[4]="LosAngeles"
start=time.time()
print "Sent Server the request at-",time.time()
ssl_sock.send(str(send_array))

data=ssl_sock.recv(1024)
print data
ssl_sock.close()
end=time.time()
print ""
print "Recieved response from server at-",end
print "Time to Process Request",end-start

