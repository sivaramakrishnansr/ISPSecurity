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




city_dict={}
file_to_read=open('/proj/SENSS/cities','r')
for line in file_to_read:
        line=line.strip()
        line=line.split(' ')
        city_dict[line[0]]=line[1]



host=sys.argv[1]
password="kru!1ualahomora"

db=MySQLdb.connect(host="localhost",port=3306,user=host,passwd=password)
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
		db.commit()
		cur.execute("SELECT COMPLETED FROM REQUEST WHERE ID=%s",str(id))
		completed=0
		for item in cur.fetchall():
			completed=int(item[0])
		if completed==1:
			file_to_write=open('output','a')
			file_to_write.write('Recieved the input from the controller Sending ACK to the Client-'+str(time.time())+"\n")
			file_to_write.close()
			connection.send(str(completed))
			break	

def get_route(request,connection):
	threads=[]
	request=eval(request)
	start_time=time.time()
	#for city,city_id in request.iteritems():
	for city in request:
		threads.append(threading.Thread(target=get_route_thread,args=(city,"1")))
	for index,t in enumerate(threads):
		t.start()
	[t.join() for t in threads]
	end_time=time.time()
	file_to_write=open('output','a')
	file_to_write.write("Time taken for route change in the server is for all-"+str(end_time-start_time)+"\n")
	file_to_write.close()

	connection.send("Changed the routes for "+str(len(threads))+" routers")
	file_to_write=open('output','a')
	file_to_write.write("SENT ACK to client at-"+str(time.time())+"\n")
	file_to_write.close()

def get_route_thread(HOST,destination):
	HOST=HOST.lower()
	HOST=HOST+".mediumtopo.senss.isi.deterlab.net"
	while True:
		print "get_route",HOST
		start_time=time.time()
		PORT="bgpd"
		password="en"
		destination="105.0.0.0"	
		tn=telnetlib.Telnet(HOST,PORT)
		data=tn.read_until("Password: ")
		print data		
		tn.write(password+"\r\n")
		data=''
		#data=tn.read_very_eager()
		data=tn.read_some()
		print data
		tn.write("sh ip bgp "+str(destination)+"\n")
		data=tn.read_some()
		print data
		data=data+tn.read_very_eager()
		print data

		if "Network not in table" in data:
			best_weight=0
			neighbor=0
			return best_weight,neighbor
		data=data.split('\n')
		neighbor=""
		best_weight=0
		best_flag=0
		#Handling the case when there is just one path which is available. In that case the same path is incremented.
		#Need to fix this point with an error message

		for i in range(0,len(data)):
        		if "best" in data[i]:
                		best_flag=1
				metric_line=data[i].split(',')
                		for item in metric_line:
                        		if "weight" in item:
                                		best_weight=item.split(' ')[2]
               			continue

        		if "Origin" in data[i]:
                		neighbor=data[i-1]
                		print neighbor
                		neighbor=neighbor.strip().split(' ')[0]
	
		if best_flag==0 and neighbor=="":
			for i in range(0,len(data)):
			        		if "Origin" in data[i]:
			                		neighbor=data[i-1]
                					print neighbor
                					neighbor=neighbor.strip().split(' ')[0]
					

		print best_weight,neighbor
		end_time=0
		if neighbor=="":
			best_weight=0
			neighbor=0
			return best_weight,neighbor
		
		if len(neighbor)!=0:
			end_time=time.time()
			file_to_write=open('output','a')
			file_to_write.write("Time taken for server to get the route query-"+str(end_time-start_time)+"\n")
			file_to_write.close()
			break
		time.sleep(0.5)

		#connection.send(str(neighbor)+" "+str(best_weight))
	return best_weight,neighbor
		




def change_route(request,connection,promote):
	threads=[]
	request=eval(request)
	start_time=time.time()
	#for city,city_id in request.iteritems():
	for city in request:
		threads.append(threading.Thread(target=change_route_thread,args=(city,city_dict[city])))
	for index,t in enumerate(threads):
		t.start()
	[t.join() for t in threads]
	end_time=time.time()
	file_to_write=open('output','a')
	file_to_write.write("Time taken for route change in the server is for all-"+str(end_time-start_time)+"\n")
	file_to_write.close()

	connection.send("Changed the routes for "+str(len(threads))+" routers")
	file_to_write=open('output','a')
	file_to_write.write("SENT ACK to client at-"+str(time.time())+"\n")
	file_to_write.close()


def change_route_thread(HOST,router):

	#if promote==True:
		original_HOST=HOST
		HOST=HOST.lower()
		HOST=HOST+".mediumtopo.senss.isi.deterlab.net"
		print "change_route",HOST
		start_time=time.time()		
		weight,neighbor=get_route_thread(original_HOST,'1')
		end_time=time.time()
		file_to_write=open('output','a')
		file_to_write.write("Time taken to get the weight and the network-"+str(end_time-start_time)+"\n")
		file_to_write.close()
		
		print "Recievd*************",weight,neighbor
		if int(weight)==0 and neighbor==0:
			#print "No such paths exist"
			#return
			neighbor="105.0.0.0"
			weight=1567
		if int(weight)==0:
			weight=1567
		else:
			weight=int(weight)+1
		weight=str(weight)
		start_time=time.time()
		#router="2"
		#HOST="losangeles"
		PORT="bgpd"
		password="en"
		router=str(router)
		tn=telnetlib.Telnet(HOST,PORT)
		tn.read_until("Password: ")
		tn.write(password+"\n")
		data=''
		data=tn.read_some()
		tn.write("enable\n")
		data=''
		data=tn.read_some()
		print data
		tn.write(password+"\n")
		data=''
		data=tn.read_some()
		print data
		tn.write("config term\n")
		data=''
		data=tn.read_some()
		print data
		tn.write("router bgp "+router+"\n")
		data=''
		data=tn.read_some()
		print data
		tn.write("neighbor "+neighbor+" weight "+weight+"\n")
		data=''
		data=tn.read_some()
		print data
		tn.write("exit\n")
		data=''
		data=tn.read_some()
		print data
		
		tn.write("write\n")
		data=''
		data=tn.read_some()
		print data

		tn.write("exit\n")
		data=''
		data=tn.read_some()
		print data

		tn.write("clear ip bgp *\n")
		data=''
		data=tn.read_some()
		print data		

		#connection.send("Route Modified")
		end_time=time.time()

		#file_to_write=open('output','a')
		#file_to_write.write("Time taken to change the path-"+str(end_time-start_time)+"\n")
		#file_to_write.close()
		#file_to_write=open('output','a')
		#file_to_write.write("Sent ACK client REQUEST-"+str(time.time())+"\n")
		#file_to_write.close()
		
		


	#if promote==False:
	#	connection.send("Dummy Demote Route")

def monitor():	
	bindsocket = socket.socket()
	bindsocket.bind(('192.168.1.9', 10023))
	bindsocket.listen(5)
	while True:
    		newsocket, fromaddr = bindsocket.accept()
    		connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
				 certfile="/proj/SENSS/certificates/cacert.pem",
				 keyfile="/proj/SENSS/certificates/cakey.pem", ssl_version=ssl.PROTOCOL_TLSv1)

		data = connstream.read(15000)
		data=eval(data)
		print data
		file_to_write=open('output','w')
		file_to_write.write('Got Client Request-'+str(time.time()))
		file_to_write.close()
		for key,value in data.iteritems():
			type=int(key)
			request=str(value)
			completed=0
			if type==4:
				#HOST,destination,connection,reply_to_client
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
			file_to_write=open('output','a')
			file_to_write.write('Sent a Client Request-'+str(time.time()))
			file_to_write.close()
			
			for item in cur.fetchall():
				last_inserted_id=int(item[0])
			print "Starting Thread for request ",last_inserted_id
			client_connection_thread=threading.Thread(target=reply_thread,args=(last_inserted_id,connstream))
			client_connection_thread.start()




init_database()
#a={"LosAngeles":2}
#change_route(str(a),1,1)
monitor()

