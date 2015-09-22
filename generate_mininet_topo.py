#Takes in the Mininet Topology and generates the zebra and bgpd files which 
#are needed for setting up Quagga



import sys

def relation(filename):
	cities={}
	file_to_open=open(filename,'r')
	for line in file_to_open:
		line=line.strip()
		if len(line)!=0 and "self.addLink(" in line:
			line=line.strip()
			line=line.split(',')
			location_1=line[0]
			location_1=location_1[13:].strip()
			location_2=line[1].strip()
			if location_1 in cities:
				cities[location_1][location_2]=1
			else:
				cities[location_1]={}
				cities[location_1][location_2]=1
			if location_2 in cities:
				cities[location_2][location_1]=1
			else:
				cities[location_2]={}
				cities[location_2][location_1]=1

	file_to_open.close()
	for key,value in cities.iteritems():
		i=1
		for city,interface in value.iteritems():
			cities[key][city]=i
			i=i+1
	return cities


#Generates the BGPD File needed for Quagga
def bgpd_file_generator(cities):
	city_router_id={}
	city_router_counter=1
	for key,value in cities.iteritems():
		city_router_id[key]=city_router_counter
		city_router_counter=city_router_counter+1
	for key,value in cities.iteritems():
		hostname="bgpd-"+str(key)
		bgpd_file=open("conf/"+hostname+".conf","w")
		bgpd_file.write("hostname "+hostname+"\n")
		bgpd_file.write("password en\n")
		bgpd_file.write("enable password en\n")
		bgpd_file.write("router bgp 1\n")
		bgpd_file.write("  bgp router-id 9.0.0."+str(city_router_id[key])+"\n")
		bgpd_file.write("  network "+str(city_router_id[key])+".0.0.0/8\n")
		for city,interface in value.iteritems():
			bgpd_file.write("  neighbor 9.0.0."+str(city_router_id[city])+" remote-as 1\n")
		bgpd_file.close()
	


#Generates the Zebra Files needed for Quagga
def zebra_file_generator(cities):
	city_router_id={}
	city_router_counter=1
	for key,value in cities.iteritems():
		city_router_id[key]=city_router_counter
		city_router_counter=city_router_counter+1

	for key,value in cities.iteritems():
		hostname=str(key)
		zebra_file=open("conf/zebra-"+hostname+".conf","w")
		zebra_file.write("hostname "+hostname+"\n")
		zebra_file.write("password en\n")
		zebra_file.write("enable password en\n")
		zebra_file.write("interface lo\n")
		zebra_file.write("  ip address 127.0.0.1/32\n")
		for city,interface in value.iteritems():
			zebra_file.write("interface "+hostname+"-eth"+str(interface)+"\n")
			zebra_file.write("  ip address "+str(city_router_id[key])+".0.0.0/24\n")
		zebra_file.close()	


#Writes the output with the interfaces on the link
def write_output(filename,cities):
	file_to_open=open(filename,'r')
	file_to_write=open(filename+'_output','w')
	for line in file_to_open:
		if len(line.strip())>0 and "self.addLink(" in line and "_h" not in line:
			original_line=line.strip()
			line=original_line.split(',')
			location_1=line[0]
			location_1=location_1[13:].strip()
			location_2=line[1].strip()
			bandwidth=line[2].strip()
			delay=line[3][:-1].strip()
			string_to_write="	self.addLink("+location_1+","+location_2+","+str(cities[location_1][location_2])+","+str(cities[location_2][location_1])+","+str(bandwidth)+","+str(delay)+")\n"
			file_to_write.write(string_to_write)
		else:
			file_to_write.write(line)	
	file_to_write.close()



def main():
	filename=sys.argv[1]
	cities=relation(filename)
	bgpd_file_generator(cities)
	zebra_file_generator(cities)
	write_output(filename,cities)


main()

