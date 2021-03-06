
file_to_write=open('nsfile.ns','w')
file_to_write.write("set ns [new Simulator]\n")
file_to_write.write("source tb_compat.tcl\n")
file_to_write.write("# Nodes\n")
input_file=open('input','r')
cities={}
city_relation={}
city_counter=1
delay_set={}
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
			delay=city_relation_str[-1]
			delay=delay.split('=')[-1][:-4]
			delay=delay[1:]
			if source_city in delay_set:
				delay_set[source_city][destination_city]=delay
			else:
				delay_set[source_city]={}
				delay_set[source_city][destination_city]=delay
			if destination_city in delay_set:	
				delay_set[destination_city][source_city]=delay
			else:
				delay_set[destination_city]={}
				delay_set[destination_city][source_city]=delay

			
			if source_city in city_relation:
				city_relation[source_city].append(destination_city)
			else:
				city_relation[source_city]=[]
				city_relation[source_city].append(destination_city)


file_to_write.write("set controller [$ns node]\n")
file_to_write.write("tb-set-node-os $controller Ubuntu1404-64-STD\n")

file_to_write.write("set client [$ns node]\n")
file_to_write.write("tb-set-node-os $client Ubuntu1404-64-STD\n")

for city,value in cities.iteritems():
	file_to_write.write("set "+city+" [$ns node]\n")
	file_to_write.write("tb-set-node-os $"+city+" Ubuntu1404-64-STD\n")


file_to_write.write("\n")
file_to_write.write("#Links\n")
link_counter=0
#10.+city+neighbor+1/2
bgpd={}

city_port_count={}
for city,item in cities.iteritems():
	city_port_count[city]=0

chosen_city=""
for city,neighbors in city_relation.iteritems():
	chose_city=city
	file_to_write.write("set link"+str(link_counter)+" [$ns duplex-link $"+str(city)+" $client 1000000Kb 100ms DropTail]\n")
	file_to_write.write("tb-set-ip-link $"+str(city)+" $link"+str(link_counter)+" 100.1.1.1\n")
	file_to_write.write("tb-set-ip-link $client $link"+str(link_counter)+" 100.1.1.2\n")
	city_port_count[city]=city_port_count[city]+1
	break

link_counter=link_counter+1


for city,neighbors in city_relation.iteritems():
	for neighbor_city in neighbors:
		if city_port_count[city]==4 or city_port_count[neighbor_city]==4:
			continue
		#file_to_write.write("set link"+str(link_counter)+" [$ns duplex-link $"+str(city)+" $"+str(neighbor_city)+" 1000000Kb "+str(float(delay_set[city][neighbor_city])+2.0)+"ms DropTail]\n")
		file_to_write.write("set link"+str(link_counter)+" [$ns duplex-link $"+str(city)+" $"+str(neighbor_city)+" 1000000Kb 0ms DropTail]\n")
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
		file_to_write.write("tb-set-ip-link $"+str(city)+" $link"+str(link_counter)+" "+str(city_ip)+"\n")
		file_to_write.write("tb-set-ip-link $"+str(neighbor_city)+" $link"+str(link_counter)+" "+str(neighbor_ip)+"\n")
		link_counter=link_counter+1
		city_port_count[city]=city_port_count[city]+1
		city_port_count[neighbor_city]=city_port_count[neighbor_city]+1





#20.0+city+1/2

#for city,number in cities.iteritems():
#	file_to_write.write("set link"+str(link_counter)+" [$ns duplex-link $"+str(city)+" $controller 1000000Kb 0ms DropTail]\n")
#	file_to_write.write("tb-set-ip-link $"+str(city)+" $link"+str(link_counter)+" 20.0."+str(cities[city])+".1\n")
#	file_to_write.write("tb-set-ip-link $controller $link"+str(link_counter)+" 20.0."+str(cities[city])+".2\n")
#	link_counter=link_counter+1

#tb-set-node-startcmd $Vienna "sudo python /proj/SENSS/start.py vienna"
for key,value in cities.iteritems():
	file_to_write.write("tb-set-node-startcmd $"+str(key)+" \"sudo python /proj/SENSS/start.py "+str(key.lower())+" "+str(chose_city)+"\"\n")


file_to_write.write("$ns rtproto Manual\n")
file_to_write.write("$ns run\n")

file_to_write.close()



'''
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

'''
