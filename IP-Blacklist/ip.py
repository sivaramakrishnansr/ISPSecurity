import git
import MySQLdb
import os
import urllib2
import time
from time import mktime
from datetime import datetime
import calendar
from subnet import subnet_from_ip,subnet_insert,subnet_remove,init_subnet,subnet_update,get_list
password="kru!1ualahomora"

db=MySQLdb.connect(host="localhost",port=3306,user="root",passwd=password)
cur=db.cursor()

def validate_ip(ip):
	ip=ip.split('.')
	if len(ip)!=4:
		return False
	if '/' in ip[3]:
		temp=ip[3].split('/')
		ip[3]=temp[0]
	for item in ip:
		temp=int(item)
		print "Temp",temp
		if temp>255:
			return False
	return True

def init_ip(folder_name):
	total_ips=0
	date_counter=0
	compare_list=[]
	file_count=0
	list=get_list()
	cur.execute('USE SENSS')
	insert_count=0;
	cmd=''
	#IP Addresses.
	for file_name in list:
		file_count=file_count+1
		if "set_file" in file_name:
			continue
		file_to_read=open(str(folder_name)+'/'+str(file_name),'r')
		count=0
		print "Doing file-",file_count,file_name
		for line in file_to_read:
			count=count+1
			if "#" in line:
				if "Date:" in line:
					data=line.split('Date:')
					time_in_epoch=calendar.timegm(datetime.fromtimestamp(mktime(time.strptime(data[1].strip(),"%a %b  %d %H:%M:%S %Z %Y"))).timetuple())
					date_counter=date_counter+1	
					compare_list.append(file_name)
				continue
			else:
				insert_count=insert_count+1
				ip_address=line.strip()
				if insert_count%10000==1:
					cmd='INSERT INTO IP(ID,FILE_NAME,IP_ADDRESS,START_TIME,NUMBER_OF_APPEARANCE,ACTIVE)VALUES(NOT NULL,\''+str(file_name)+'\',\''+str(ip_address)+'\',\''+str(time_in_epoch)+'\',1,1)'
				else:
					cmd=cmd+","+'(NOT NULL,\''+str(file_name)+'\',\''+str(ip_address)+'\',\''+str(time_in_epoch)+'\',1,1)'
				if insert_count%10000==0:
					cur.execute(cmd)
					db.commit()
					print "Done with "+str(total_ips)+" /3437022"
			total_ips=total_ips+1
	if insert_count%10000!=0:
		cur.execute(cmd)
		db.commit()
	

	#SUBNET 

	print total_ips

def compare_and_update(old_folder,new_folder):
	list=get_list()
	count=0
	cur.execute('USE SENSS')
	new_ip=0
	old_ip=0
	total_add=0
	total_remove=0
	for file_name in list:
		file_to_read=open(str(new_folder)+"/"+file_name,'r')
		print "Doing",file_name
		for line in file_to_read:
			if "#" in line:
				if "Date:" in line:
					data=line.split('Date:')
					time_in_epoch=calendar.timegm(datetime.fromtimestamp(mktime(time.strptime(data[1].strip(),"%a %b  %d %H:%M:%S %Z %Y"))).timetuple())
				continue
		
		with open(str(old_folder)+"/"+file_name) as f:
		    temp=[]
		    for line in f:
		    	if '#' in line:
		    		continue
		    	temp.append(line.strip())
		    t1s = set(temp)
		
		with open(str(new_folder)+'/'+file_name) as f:
		    temp=[]
		    for line in f:
		    	if '#' in line:
		    		continue
		    	temp.append(line.strip())
		    t2s = set(temp)
		
		remove_ip=[]
		add_ip=[]
		for diff in t1s-t2s:
		    remove_ip.append(diff)

		for diff in t2s-t1s:
			add_ip.append(diff)
		#ID 
		#FILE_NAME 
		#IP_ADDRESS 
		#NUMBER_OF_APPEARANCE 
		#START_TIME 
		#DURATION 
		#ACTIVE 
		insert_count=0
		for ip in add_ip:
			cur.execute('SELECT ID FROM IP WHERE IP_ADDRESS=%s and FILE_NAME=%s',(str(ip),str(file_name)))
			if not cur.rowcount:
				insert_count=insert_count+1
				ip_address=line.strip()
				if insert_count%10000==1:
					cmd='INSERT INTO IP(ID,FILE_NAME,IP_ADDRESS,START_TIME,NUMBER_OF_APPEARANCE,ACTIVE)VALUES(NOT NULL,\''+str(file_name)+'\',\''+str(ip_address)+'\',\''+str(time_in_epoch)+'\',1,1)'
				else:
					cmd=cmd+","+'(NOT NULL,\''+str(file_name)+'\',\''+str(ip_address)+'\',\''+str(time_in_epoch)+'\',1,1)'
				if insert_count%10000==0:
					cur.execute(cmd)
					db.commit()
			else:
				for item in cur:
					cur.execute('UPDATE IP SET START_TIME=%s,ACTIVE=1 WHERE ID=%s',(str(time_in_epoch),str(item[0])))
					db.commit()
		if insert_count%10000!=0:
			cur.execute(cmd)
			db.commit()

		for ip in remove_ip:
			cur.execute('SELECT ID,START_TIME,NUMBER_OF_APPEARANCE,DURATION FROM IP WHERE IP_ADDRESS=%s AND FILE_NAME=%s',(str(ip),str(file_name)))
			for item in cur.fetchall():
				id=int(item[0])
				start_time=int(item[1])
				number_of_appearance=int(item[2])
				number_of_appearance=number_of_appearance+1
				end_time=int(calendar.timegm(time.gmtime()))
				duration_string=str(item[3])
				duration=int(end_time)-start_time
				duration_string=duration_string+","+str(duration)
				cur.execute("UPDATE IP SET NUMBER_OF_APPEARANCE=%s,DURATION=%s,ACTIVE=0 WHERE ID=%s",(str(number_of_appearance),str(duration_string),str(id)))
				db.commit()				

	print total_add,total_remove


	return old_ip,new_ip
