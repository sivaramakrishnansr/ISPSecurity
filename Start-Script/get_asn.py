import telnetlib
def get_values(HOST):
 	PORT=2605
        password="en"
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
        #router bgp 9090
        tn.write("router bgp 9090\n")
        data=''
        data=tn.read_some()
        print data
        router=''
        router=data.split(' ')
        router=router[-1]
	print router
	tn.close()
	return router

asn_dict={}
file_to_read=open('nsfile.ns','r')
for line in file_to_read:
        if 'tb-set-node-startcmd' in line:
                line=line.strip()
                city_string=line.split(' ')
                city_string=city_string[1][1:]
                command_string=line.split('"')
                command_string=command_string[1]
                connect_to_node=city_string+".cogent.senss.isi.deterlab.net"
		try:
			value=get_values(connect_to_node)
			if value !=None:
				file_to_write=open('asn_values','a')
				file_to_write.write(str(city_string)+","+str(value)+"\n")
				file_to_write.close()	

		except:
			a=1
