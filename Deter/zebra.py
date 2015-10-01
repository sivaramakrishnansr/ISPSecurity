#Generates the zebra file for quagga
import netifaces
interface_list = netifaces.interfaces()
interface_dict={}
for interface in interface_list:
	try:
		address=netifaces.ifaddresses(interface)
		interface_dict[interface]=address[netifaces.AF_INET][0]['addr']
	except:
		a=1	

file_to_write=open('zebra.conf','w')
file_to_write.write('hostname zebra\n')
file_to_write.write('password en\n')
file_to_write.write('enable password en\n')

for key,value in interface_dict.iteritems():
	file_to_write.write('interface '+str(key)+"\n")
	file_to_write.write('	ip address '+str(value)+'/24\n')

file_to_write.close()
