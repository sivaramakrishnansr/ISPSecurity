#Takes in the Mininet Topology and generates the zebra and bgpd files which 
#are needed for setting up Quagga
import sys
def relation(filename):
	cities={}
	file_to_open=open(filename,'r')
	for line in file_to_open:
		line = line.replace('\'', '').strip()
		if len(line)!=0 and "self.addLink(" in line:
			line=line.strip()
			line=line.split(',')
			location_1=line[0]
			location_1=location_1[13:].strip()
			location_2=line[1].strip()
			if location_1 in cities:
				cities[location_1].add(location_2)
			else:
				cities[location_1]=set()
				cities[location_1].add(location_2)
			if location_2 in cities:
				cities[location_2].add(location_1)
			else:
				cities[location_2]=set()
				cities[location_2].add(location_1)
	

	file_to_open.close()
	src_dst={}
	count=0
	for key,value in cities.iteritems():
		count=count+1
		cities[key]=list(cities[key])
		src_dst[key]=count

	#Creating the Master City Structure Which contains:-
	#	a)Router
	#		a.1)ASN
	#		a.2)Neighbor
	#			a.2.1)Interface
	#			a.2.1)IP - Format of Source - Destination IP
	#		a.3)Network
	#		a.4)Local IP	

	network_counter=1
	master_cities={}
	for key,value in cities.iteritems():

			master_cities[key]={}
			master_cities[key]['ASN']=1
			master_cities[key]['Network']=str(network_counter)+".255.0.0/8"
			master_cities[key]['Neighbors']={}
			master_cities[key]['Local_IP']=str(network_counter)+".0.0.254/24"
			interface_ip_count=1
			for neighbors in value:
				master_cities[key]['Neighbors'][neighbors]={}
				interface="eth"+str(interface_ip_count)
				ip=str(src_dst[key])+".0."+str(src_dst[neighbors])+"."+str(interface_ip_count)
				master_cities[key]['Neighbors'][neighbors]['Interface']=interface
				master_cities[key]['Neighbors'][neighbors]['IP']=ip
				interface_ip_count=interface_ip_count+1
			network_counter=network_counter+1

	for key,value in cities.iteritems():
		for item in value:

			ip_addr_src=master_cities[key]['Neighbors'][item]['IP']
			ip_addr_dst=master_cities[item]['Neighbors'][key]['IP']
			ip_addr_src= ip_addr_src.split('.')
			ip_addr_dst= ip_addr_dst.split('.')
			for i in range(0,3):
				ip_addr_src[i]=ip_addr_dst[i]
			ip_addr_src[3]='1'
			ip_addr_dst[3]='2'
			ip_addr_src='.'.join(ip_addr_src)
			ip_addr_dst='.'.join(ip_addr_dst)
			master_cities[key]['Neighbors'][item]['IP']=ip_addr_src
			master_cities[item]['Neighbors'][key]['IP']=ip_addr_dst
			
	
	return cities,master_cities,src_dst


def pretty_print(master_cities,indent=0):
	for key, value in master_cities.iteritems():
		print '\t' * indent + str(key)
		if isinstance(value, dict):
			 pretty_print(value, indent+1)
		else:
			 print '\t' * (indent+1) + str(value)
	

#Generates the BGPD File needed for Quagga
def bgpd_file_generator(cities,master_cities,src_dst):
		for key,value in cities.iteritems():
			hostname="bgpd-"+str(key)
			bgpd_file=open("conf/"+hostname+".conf",'w')
			bgpd_file.write("hostname "+hostname+"\n")
			bgpd_file.write("password en\n")
			bgpd_file.write("enable password en\n")
			bgpd_file.write("router bgp "+str(src_dst[key])+"\n")
			bgpd_file.write("  network "+str(master_cities[key]['Network'])+"\n")
			for neighbor in value:
				bgpd_file.write("  neighbor "+master_cities[neighbor]['Neighbors'][key]['IP']+" remote-as "+str(src_dst[neighbor])+"\n")
			bgpd_file.close()	
	


#Generates the Zebra Files needed for Quagga
def zebra_file_generator(cities,master_cities):
	
	for key,value in cities.iteritems():
		hostname=str(key)
		zebra_file=open("conf/zebra-"+hostname+".conf",'w')
		zebra_file.write("hostname "+hostname+"\n")
		zebra_file.write("password en\n")
		zebra_file.write("enable password en\n")
		zebra_file.write("interface lo\n")
		zebra_file.write("  ip address 127.0.0.1/32\n")
		zebra_file.write("interface "+str(key)+"-eth0\n")
		zebra_file.write("  ip address "+master_cities[key]['Local_IP']+"\n")
		for item in value:
			zebra_file.write("interface "+hostname+"-"+master_cities[key]['Neighbors'][item]['Interface']+"\n")
			zebra_file.write("  ip address "+str(master_cities[key]['Neighbors'][item]['IP'])+"/24\n")
		zebra_file.close()	


#Writes the output with the interfaces on the link
def write_output(filename,master_cities):
	file_to_open=open(filename,'r')
	file_to_write=open("output",'w')

	for line in file_to_open:
		original_line=line.strip()
		if len(original_line) > 0:
			line=original_line.split(',')
			source=line[0][13:].strip()
			source = source.replace('\'', '').strip()
			destination=line[1].strip()
			destination = destination.replace('\'', '').strip()
			original_line=original_line.split(',')
			original_line.insert(2,master_cities[source]['Neighbors'][destination]['Interface'][-1])
			original_line.insert(3,master_cities[destination]['Neighbors'][source]['Interface'][-1])
			original_line=','.join(original_line)
			file_to_write.write(original_line+"\n")
			print original_line
	file_to_open.close()	
	file_to_write.close()	
def main():
	filename=sys.argv[1]
	cities,master_cities,src_dst=relation(filename)
	bgpd_file_generator(cities,master_cities,src_dst)
	zebra_file_generator(cities,master_cities)
	write_output(filename,master_cities)

main()

