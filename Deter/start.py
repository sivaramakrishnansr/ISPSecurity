import os
import time
import sys
#Generates the Daemon file for Quagga
file_to_write=open('/etc/quagga/daemons','w')
file_to_write.write('zebra=yes\n')
file_to_write.write('bgpd=yes\n')
file_to_write.write('ospfd=no\n')
file_to_write.write('ospf6d=no\n')
file_to_write.write('ripd=no\n')
file_to_write.write('ripngd=no\n')
file_to_write.write('isisd=no\n')
file_to_write.close()


#Generates the BGPD file for quagga
input_file=open('input','r')
cities={}
city_relation={}
city_counter=1

for line in input_file:
	line=line.strip()
	if len(line)!=0:
		#Getting the Routers/ISP
		if "self.addSwitch" in line:
			city_line=line.split('=')
			cities[city_line[0].strip()]=city_counter
			city_counter=city_counter+1
		#Getting the Relationship between the cities
		if "self.addLink" in line:
			city_relation_str=line.split(',')
			source_city=city_relation_str[0][14:].strip()
			destination_city=city_relation_str[1].strip()
			if source_city in city_relation:
				city_relation[source_city].append(destination_city)
			else:
				city_relation[source_city]=[]
				city_relation[source_city].append(destination_city)

link_counter=0
#10.+city+neighbor+1/2
bgpd={}

for city,neighbors in city_relation.iteritems():
	for neighbor_city in neighbors:
		city_ip="10."+str(cities[city])+"."+str(cities[neighbor_city])+".1"
		neighbor_ip="10."+str(cities[city])+"."+str(cities[neighbor_city])+".2"
		if city in bgpd:
			bgpd[city][neighbor_ip]=cities[neighbor_city]
		else:
			bgpd[city]={}
			bgpd[city][neighbor_ip]=cities[neighbor_city]
		if neighbor_city in bgpd:
			bgpd[neighbor_city][city_ip]=cities[city]
		else:
			bgpd[neighbor_city]={}
			bgpd[neighbor_city][city_ip]=cities[city]
		link_counter=link_counter+1


#20.0+city+1/2
for key,value in bgpd.iteritems():
	file_to_write=open("/users/satyaman/conf/"+str(key.lower())+".conf","w")
	file_to_write.write("hostname "+str(key)+"\n")
	file_to_write.write("password en\n")
	file_to_write.write("enable password en\n")
	file_to_write.write("router bgp "+str(cities[key])+"\n")
	file_to_write.write(" network "+str(cities[key]+100)+".0.0.0/8\n")
	for ip,city_id in value.iteritems():
		file_to_write.write(" neighbor "+ip+" remote-as "+str(city_id)+"\n")
	file_to_write.close()

#Need to copy the conf file and move it into /etc/quagga/
city=sys.argv[1]
file_name=str(city)+".conf"
os.system('sudo cp /users/satyaman/conf/'+file_name+' /etc/quagga/bgpd.conf')

#Need to install netifaces package
os.system('sudo apt-get update')
os.system('sudo dpkg -i /proj/SENSS/python-netifaces_0.6-2ubuntu1_amd64.deb')

#Need to install openvswitch
#os.system('sudo apt-get install openvswitch-switch')

time.sleep(3)
import netifaces
interface_list = netifaces.interfaces()
interface_dict={}
for interface in interface_list:
	try:
		address=netifaces.ifaddresses(interface)
		interface_dict[interface]=address[netifaces.AF_INET][0]['addr']
	except:
		a=1	
#writing the zebra file
file_to_write=open('/etc/quagga/zebra.conf','w')
file_to_write.write('hostname zebra\n')
file_to_write.write('password en\n')
file_to_write.write('enable password en\n')

for key,value in interface_dict.iteritems():
	file_to_write.write('interface '+str(key)+"\n")
	file_to_write.write('	ip address '+str(value)+'/24\n')

file_to_write.close()


#Restart Quagga
os.system('sudo service quagga restart')
	
