import os
import subprocess
import time
import sys
import socket

#Change the chosen one IP

chosen_city=str(sys.argv[2])
chosen_city=str(chosen_city.lower())

ip_list = []
ais = socket.getaddrinfo(chosen_city+".cogentcore.senss.isi.deterlab.net",0,0,0,0)
for result in ais:
  ip_list.append(result[-1][0])
ip_list = list(set(ip_list))
controller_ip=str(ip_list[0])


#print "Removing Existing Quagga Config Files"
cmd_to_execute="sudo rm /etc/quagga/*"
#proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
proc = subprocess.Popen(cmd_to_execute,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
proc.wait()




#Need to install netifaces package
#print "Installing the Netifaces Package"
cmd_to_execute='sudo apt-get update'
proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

proc.wait()


#cmd_to_execute='sudo dpkg -i /proj/SENSS/python-netifaces_0.6-2ubuntu1_amd64.deb'
cmd_to_execute='sudo dpkg -i /proj/SENSS/python-netifaces_0.8-3build1_i386.deb'
proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

proc.wait()



#Installing openvswitch on every node

#proc = subprocess.Popen('apt-get install -y openvswitch-switch', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
#proc.wait()

print "Installing the OpenvSwitch"
cmd_to_execute="sudo apt-get --assume-yes install openvswitch-switch"
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
proc.wait()



cmd_to_execute="mkdir /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])
os.system(cmd_to_execute)
#proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)
#proc.wait()

cmd_to_execute="cp -r /users/satyaman/openvswitch/openvswitch-2.4.0/ /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])
print cmd_to_execute
#os.system(cmd_to_execute)
os.system(cmd_to_execute)

#proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#proc.wait()

#print "Preset"
cmd_to_execute="cd /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2]) + "/openvswitch-2.4.0/ && sudo make distclean"
print cmd_to_execute
os.system(cmd_to_execute)

#proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#proc.wait()


#print "Configuring"
cmd_to_execute="cd /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])+"/openvswitch-2.4.0/  && sudo ./configure --prefix=/usr --with-linux=/lib/modules/`uname -r`/build"
print cmd_to_execute
os.system(cmd_to_execute)

#proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#proc.wait()

#print "Running make"
cmd_to_execute="cd /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])+"/openvswitch-2.4.0/ && sudo make"
print cmd_to_execute
os.system(cmd_to_execute)

#proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#proc.wait()

#print "Running make install"
cmd_to_execute="cd /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])+"/openvswitch-2.4.0/ && sudo make install"
print cmd_to_execute
os.system(cmd_to_execute)

#proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#proc.wait()

#print "Running modules_install"
cmd_to_execute="cd /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])+"/openvswitch-2.4.0/ && sudo make modules_install"
print cmd_to_execute
os.system(cmd_to_execute)

#proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#proc.wait()

#print "Setting depmod to 0"
cmd_to_execute="sudo depmod -a"
print cmd_to_execute
proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
proc.wait()


cmd_to_execute="sudo rm -rf cd /users/satyaman/"+str(sys.argv[1])+str(sys.argv[2])
print cmd_to_execute
proc = subprocess.Popen(cmd_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
proc.wait()


#print "Restarting the switch"
cmd_to_execute="sudo /etc/init.d/openvswitch-switch start"
print cmd_to_execute

proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()


#print "Adding the bridge br0"
cmd_to_execute="sudo ovs-vsctl add-br br0"
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()

#print "Setting OpenFlow13 as the protocol to the bridge"
cmd_to_execute="sudo ovs-vsctl set Bridge br0 protocols=OpenFlow13"
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()

#print "Connecting the controller to the bridge at IP",controller_ip
cmd_to_execute="sudo ovs-vsctl set-controller br0 tcp:"+controller_ip+":6633"
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()







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


#print "Installing Quagga"
cmd_to_execute="sudo apt-get install quagga"
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()


#Generates the Debian Config file to be Telnet'd from different locations
file_to_write=open('/etc/quagga/debian.conf','w')
file_to_write.write('vtysh_enable=yes\n')
file_to_write.write('zebra_options="  --daemon -A 127.0.0.1"\n')
file_to_write.write('bgpd_options="   --daemon "\n')
file_to_write.write('ospfd_options="  --daemon -A 127.0.0.1"\n')
file_to_write.write('ospf6d_options=" --daemon -A ::1"\n')
file_to_write.write('ripd_options="   --daemon -A 127.0.0.1"\n')
file_to_write.write('ripngd_options=" --daemon -A ::1"\n')
file_to_write.write('isisd_options="  --daemon -A 127.0.0.1"\n')
file_to_write.write('babeld_options=" --daemon -A 127.0.0.1"\n')
file_to_write.write('watchquagga_enable=yes\n')
file_to_write.write('watchquagga_options=(--daemon)\n')
file_to_write.close()


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
input_file=open('/proj/SENSS/input','r')
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
	file_to_write.write(" network "+str(cities[key])+".0.0.0/8\n")
	for ip,city_id in value.iteritems():
		file_to_write.write(" neighbor "+ip+" remote-as "+str(city_id)+"\n")
	file_to_write.close()

#Need to copy the conf file and move it into /etc/quagga/
city=sys.argv[1]
file_name=str(city)+".conf"

cmd_to_execute='sudo cp /users/satyaman/conf/'+file_name+' /etc/quagga/bgpd.conf'
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()


#writing the zebra file




#print "Writing the Quagga Config Files"
file_to_write=open('/etc/quagga/zebra.conf','w')
file_to_write.write('hostname zebra\n')
file_to_write.write('password en\n')
file_to_write.write('enable password en\n')

for key,value in interface_dict.iteritems():
	file_to_write.write('interface '+str(key)+"\n")
	file_to_write.write('	ip address '+str(value)+'/24\n')

file_to_write.close()

file_to_write=open('/proj/SENSS/cities','w')
for key,value in cities.iteritems():
	file_to_write.write(str(key)+" "+str(value)+"\n")
file_to_write.close()
	

#Restart Quagga
#print "Restarting Quagga"

cmd_to_execute='sudo service quagga restart'
proc = subprocess.Popen(cmd_to_execute, shell=True, stdin=None, stdout=None, stderr=None, executable=None)

proc.wait()

#print "Done .."
