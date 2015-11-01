#USed for setting the controller's IP


import os
import select
import paramiko
import time
count=0
exception_list=[]

file_to_read=open('nsfile.ns','r')
for line in file_to_read:
	if 'tb-set-node-startcmd' in line:
		line=line.strip()
		city_string=line.split(' ')
		city_string=city_string[1][1:]
		command_string=line.split('"')

		os.system("ssh "+city_string+".cogent.senss sudo ovs-vsctl set-controller br0 tcp:192.168.0.59:6633")
		print city_string


for item in exception_list:
	print item

