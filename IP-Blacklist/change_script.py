#Script to update the files from this repository https://github.com/ktsaou/blocklist-ipsets.git
#Updates the database if required.

import git
import MySQLdb
import os
import urllib2
import time
from time import mktime
from datetime import datetime
import calendar
#Need to check if it has been cloned already or not.


password="kru!1ualahomora"

db=MySQLdb.connect(host="localhost",port=3306,user="root",passwd=password)
cur=db.cursor()



def init():
	global db,cur
	try: 
		cur.execute("CREATE DATABASE SENSS")
		print "Database SENSS created"
	except:
		print "Database SENSS already exists"

	
	cur.execute("USE SENSS")

	try:
		cur.execute("CREATE TABLE IP(ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,FILE_NAME VARCHAR(50),IP_ADDRESS VARCHAR(40),NUMBER_OF_OCCURANCES INT)")
		print "Table IP created"
	except:
		print "Table IP already exists"

#https://raw.githubusercontent.com/ktsaou/blocklist-ipsets/master/ri_connect_proxies_30d.ipset
def get_list():
	list=[]
	file_to_read=open('list','r')
	for item in file_to_read:
		item=item.split('\t')
		item=item[0].strip()
		list.append(item)
	return list

def download_files(folder_name,download):
	list=get_list()
	os.system('mkdir '+str(folder_name))
	if download:
		for item in list:
			print "Downloading ",item,str(list.index(item))," of ",str(len(list))
			url="https://raw.githubusercontent.com/ktsaou/blocklist-ipsets/master/"+item
			file_downloaded = urllib2.urlopen(url)
			output = open(str(folder_name)+'/'+item,'w')
			output.write(file_downloaded.read())
			output.close()

#This function updates all the IPs into the database
def init_data(folder_name):
	total_ips=0
	date_counter=0
	compare_list=[]
	file_count=0
	list=get_list()
	cur.execute('USE SENSS')
	for item in list:
		file_count=file_count+1
		if "set_file" in item:
			continue
		file_to_read=open(str(folder_name)+'/'+str(item),'r')
		count=0
		print "Doing file-",file_count,item
		for line in file_to_read:
			count=count+1
			if "#" in line:
				if "Date:" in line:
					data=line.split('Date:')
					time_in_epoch=calendar.timegm(datetime.fromtimestamp(mktime(time.strptime(data[1].strip(),"%a %b  %d %H:%M:%S %Z %Y"))).timetuple())
					date_counter=date_counter+1	
					compare_list.append(item)
				continue
			else:
				ip_address=line.strip()
				cur.execute('INSERT INTO IP(ID,FILE_NAME,IP_ADDRESS,START_TIME,NUMBER_OF_OCCURANCES,ACTIVE)VALUES(NOT NULL,%s,%s,%s,0,1)',(str(item),ip_address,time_in_epoch))
				db.commit()
				print "Done with "+str(total_ips)+" /3437022"	
			total_ips=total_ips+1
	print total_ips


def compare_and_update(old_folder,new_folder):
	list=get_list()
	count=0
	cur.execute('USE SENSS')
	new_ip=0
	old_ip=0
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
		
		for ip_address in remove_ip:
			cmd='SELECT ID,NUMBER_OF_OCCURANCES FROM IP WHERE IP_ADDRESS=\''+str(ip_address)+'\' AND FILE_NAME=\''+str(file_name)+'\''
			print cmd
			cur.execute(cmd)
			if not cur.rowcount:
				cmd='INSERT INTO IP(ID,FILE_NAME,NUMBER_OF_OCCURANCES,IP_ADDRESS)VALUES(NULL,\''+str(file_name)+'\',1,\''+str(ip_address)+'\')'
				print cmd
				cur.execute(cmd)	
				db.commit()
				new_ip=new_ip+1
			else:
				for row in cur:
					id=row[0]
					number_of_occurances=int(row[1])
					number_of_occurances=number_of_occurances+1
					cmd='UPDATE IP SET NUMBER_OF_OCCURANCES=\''+str(number_of_occurances)+'\' WHERE ID\''+str(id)+'\''
					print cmd
					cur.execute(cmd)
					db.commit()
				old_ip=old_ip+1
		print "******************************************"
		print file_name,"comparing",old_folder,"and",new_folder
		print "Repeated Offender-",old_ip
		print "First time Offender-",new_ip
		print "******************************************"
		print
	return old_ip,new_ip
	



	

#Initialises the datafiles
init()
iteration_count=4
#old ip - existing ip - which is coming into the set of ips again
#new ip - first time the ip is getting out of the list
while True:
	#Downloads the file from the respective URLs belonging to the list
	download_files(iteration_count,True)
	#Compares the previous and the present list and gets the difference
	old_ip,new_ip=compare_and_update(iteration_count-1,iteration_count)
	iteration_count=iteration_count+1
	file_to_write=open('logs','a')
	file_to_write.write(str(iteration_count)+","+str(old_ip)+","+str(new_ip)+"\n")
	file_to_write.close()
