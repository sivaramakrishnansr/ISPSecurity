import os
import select
import paramiko
count=0
exception_list=[]

file_to_read=open('nsfile.ns','r')
for line in file_to_read:
	if 'tb-set-node-startcmd' in line:
		count=count+1
		line=line.strip()
		city_string=line.split(' ')
		city_string=city_string[1][1:]
		command_string=line.split('"')
		command_string=command_string[1]
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
		connect_to_node=city_string+".cogent.senss.isi.deterlab.net"
		#os.system('ssh-keygen -R '+connect_to_node)
		try:
			ssh.connect(connect_to_node)
			#stdin, stdout, stderr = ssh.exec_command('nohup sudo python /users/satyaman/ISPSecurity/Deter/Containers/change.py&')
			print "Conneceted to",city_string,count,"/183"
			'''
			print command_string
			transport = ssh.get_transport()
			channel = transport.open_session()
			channel.exec_command(command_string)
			while True:
				if channel.exit_status_ready():
        				break
  				rl, wl, xl = select.select([channel],[],[],0.0)
  				if len(rl) > 0:
				      	a=1
			
					print channel.recv(1024).strip()
			'''
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

