import telnetlib
import time
def telnet_into_node(HOST):
	password="en"
	PORT=2605	
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
        city=tn.read_some()
        print city
        tn.write("sh ip bgp\n")
        data=''
	count=1
	print
	print
	print
	start=time.time()
	while True:
		count=count+1
        	d=tn.read_some()
		data=data+d
		if count==10:
			break
		

	print "****************************************************"
	data=data.split('\n')
	for i in xrange(0,len(data)):
		if "Network" in data[i] and "Next Hop" in data[i]:
			network=data[i+1].strip()
			network=' '.join(network.split())
			network=network.split(' ')
			network=network[1]
			city=city.split('\n')
			city=city[1].strip()[:-1]
			print city,network
			file_to_write=open('city_to_network','a')
			file_to_write.write(city+","+network+"\n")
			file_to_write.close()

file_to_read=open('nsfile.ns','r')
count=0
for line in file_to_read:
	if "tb-set-node-startcmd" in line:
		count=count+1
		line=line.strip()
		line=line.split(' ')
		line=line[1]
		line=line[1:]
		city=line+".cogent.senss.isi.deterlab.net"
		try:
			telnet_into_node(city)
		except:
			print "Skipped"
file_to_read.close()
