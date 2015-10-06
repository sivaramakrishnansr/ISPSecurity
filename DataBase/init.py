import socket
import time
import ssl
import MySQLdb
import sys
import threading
import getpass
import telnetlib

import getpass
import telnetlib
import sys
from optparse import OptionParser
import time








host=sys.argv[1]
password=""

db=MySQLdb.connect(host="192.168.3.178",port=3306,user=host,passwd=password)
cur=db.cursor()




def init_database():
	try: 
		cur.execute("CREATE DATABASE SENSS")
		print "Database SENSS created"
	except:
		print "Database SENSS already exists"

	cur.execute("USE SENSS")
	try:
		cur.execute("CREATE TABLE REQUEST(ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,TYPE INT,REQUEST VARCHAR(1000),RESULT VARCHAR(1000),COMPLETED INT)")
		print "Table REQUEST created"
	except:
		print "Table REQUEST already exists"



def reply_thread(id,connection):
	while True:
		cur.execute("SELECT COMPLETED FROM REQUEST WHERE ID=%s",id)
		for item in cur.fetchall():
			completed=int(item[0])
		if completed==0:
			connection.send(str(completed))
			break	

def get_route(request,connection,reply_to_client):
	while True:     	
		HOST="losangeles"
		PORT="bgpd"
		password="en"
		destination="101.0.0.0"	
		tn=telnetlib.Telnet(HOST,PORT)
		data=tn.read_until("Password: ")
		print data		
		tn.write(password+"\r\n")
		data=''
		data=tn.read_very_eager()
		print data
		tn.write("sh ip bgp "+str(destination)+"\n")
		data=tn.read_some()
		print data
		data=data+tn.read_very_eager()
		print data
		data=data.split('\n')
		neighbor=""
		best_weight=0
		for i in range(0,len(data)):
        		if "best" in data[i]:
                		metric_line=data[i].split(',')
                		for item in metric_line:
                        		if "weight" in item:
                                		best_weight=item.split(' ')[2]
               			continue

        		if "Origin" in data[i]:
                		neighbor=data[i-1]
                		print neighbor
                		neighbor=neighbor.strip().split(' ')[0]
	
		print best_weight,neighbor
		if len(neighbor)!=0:
			break
		time.sleep(0.5)
	if reply_to_client == True:
		connection.send(str(neighbor)+" "+str(best_weight))
	return best_weight,neighbor
		




def change_route(request,connection,promote):
	if promote==True:
		connection.send("Dummy Promote Route")
		

		#Neighbor whose path which needs to be changed
		neighbor=1
		#Adding a larger value
		weight=1205
		
		router="10.1.2.3"
		





	if promote==False:
		connection.send("Dummy Demote Route")


def monitor():	
	bindsocket = socket.socket()
	bindsocket.bind(('192.168.3.178', 10023))
	bindsocket.listen(5)
	while True:
    		newsocket, fromaddr = bindsocket.accept()
    		connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
				 certfile="/proj/SENSS/certificates/cacert.pem",
				 keyfile="/proj/SENSS/certificates/cakey.pem", ssl_version=ssl.PROTOCOL_TLSv1)

		data = connstream.read()
		data=eval(data)
		for key,value in data.iteritems():
			type=int(key)
			request=str(value)
			completed=0
			if type==4:
				client_connection_thread=threading.Thread(target=get_route,args=(request,connstream))
				client_connection_thread.start()
				continue
			if type==5:
				client_connection_thread=threading.Thread(target=change_route,args=(request,connstream,True))
				client_connection_thread.start()
				continue
			if type==6:
				client_connection_thread=threading.Thread(target=change_route,args=(request,connstream,False))
				client_connection_thread.start()
				continue
				
			cur.execute("INSERT INTO REQUEST(ID,TYPE,REQUEST,COMPLETED) VALUES(NULL,%s,%s,%s)",(type,request,completed))
			db.commit()
			cur.execute('SELECT last_insert_id()')	
			for item in cur.fetchall():
				last_inserted_id=int(item[0])
			print "Starting Thread for request ",last_inserted_id
			client_connection_thread=threading.Thread(target=reply_thread,args=(last_inserted_id,connstream))
			client_connection_thread.start()




init_database()

print get_route('1','1',False)
monitor()

