#Installs Screen and Installs OpenVSwitch on that


import time
import os
import select
import paramiko
count=0
exception_list=[]

file_to_read=open('nsfile.ns','r')
for line in file_to_read:
	if 'tb-set-node-startcmd' in line:
		count=count+1
		if count>=4:
			continue
		#if count%20==0:
		#	time.sleep(25*60)
		line=line.strip()
		city_string=line.split(' ')
		city_string=city_string[1][1:]
		command_string=line.split('"')
		command_string="screen -d -m "+command_string[1] 
		ssh = paramiko.SSHClient()
		paramiko.util.log_to_file("filename.log")
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
		connect_to_node=city_string+".cogent.senss.isi.deterlab.net"
		os.system('ssh-keygen -R '+connect_to_node)
		
		#Command to install screen
		os.system('ssh -o StrictHostKeyChecking=no '+city_string+'.cogent.senss sudo apt-get install screen')

		try:
			print "Conneceted to",city_string,count,"/183"
			print command_string
			ssh.connect(connect_to_node)
			ssh.exec_command(command_string)
			ssh.close()
		except:
			exception_list.append(connect_to_node)
		file_to_write=open('init1','a')
		file_to_write.write('done with '+str(count)+"\n")
		file_to_write.close()

print
print
for item in exception_list:
	print item

