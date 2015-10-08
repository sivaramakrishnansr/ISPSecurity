import sys
import socket, ssl, pprint
import time
start=time.time()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ssl_sock = ssl.wrap_socket(s,
                           ca_certs="/proj/SENSS/certificates/server-chain.crt",
                           cert_reqs=ssl.CERT_REQUIRED)

ssl_sock.connect(('192.168.1.9', 10023))
end=time.time()
rpki_validation=end-start
print "Time to connect via SSL and RPKI",end-start
#Different types of Request
#1 - Observation On a Match Type
#2 - Add Flow - On a Match Type 
#3 - Remove Flow - On Match Type
#4 - Get Route - No data
#5 - Promote Route - No data
#6 - Demote Route - No data
city_array=[]
file_to_read=open('/proj/SENSS/cities','r')
for line in file_to_read:
	line=line.strip()
	line=line.split(' ')
	city_array.append(line[0])	


send_array=[]
count=0	
break_flag=0
while True:
	for item in city_array:
		if count==int(sys.argv[1]):
			break_flag=1
			break
		send_array.append(item)
		count=count+1
	if break_flag==1:
		break

print send_array
print len(send_array)

request_array={}
#request_array[1]=send_array
request_array[1]=str(sys.argv[1])
start=time.time()
print "Sent Server the request at-",time.time()
ssl_sock.send(str(request_array))

data=ssl_sock.recv(1024)
print data
ssl_sock.close()
end=time.time()
print ""
print "Recieved response from server at-",end
print "Time to Process Request",end-start
process_request=end-start
file_to_write=open('stats','a')
file_to_write.write(str(sys.argv[1])+" "+str(rpki_validation)+" "+str(process_request)+"\n")


