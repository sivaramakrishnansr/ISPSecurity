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
from subnet import subnet_from_ip,subnet_insert,subnet_remove,init_subnet,subnet_update,get_list
from ip import validate_ip,init_ip,compare_and_update

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
	#IP Table
	try:
		cur.execute("CREATE TABLE IP(ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,FILE_NAME VARCHAR(50),IP_ADDRESS VARCHAR(40),NUMBER_OF_APPEARANCE INT,START_TIME VARCHAR(20),DURATION VARCHAR(500),ACTIVE INT)")
		print "Table IP created"
	except:
		print "Table IP already exists"

	#SUBNET Table
	try:
		cur.execute("CREATE TABLE SUBNET(ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,SUBNET VARCHAR(40),COUNT_HISTORY VARCHAR(8000),START_TIME VARCHAR(20),DURATION VARCHAR(500),ACTIVE INT,NUMBER_OF_APPEARANCE INT)")
		print "Table SUBNET created"
	except:
		print "Table SUBNET already exists"

	#ASN Table
	try:
		cur.execute("CREATE TABLE ASN(ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,ASN VARCHAR(40),COUNT_HISTORY VARCHAR(8000),START_TIME VARCHAR(20),DURATION VARCHAR(500),ACTIVE INT,NUMBER_OF_APPEARANCE INT)")
		print "Table ASN created"
	except:
		print "Table ASN already exists"


def download_files(folder_name,download):
	#https://raw.githubusercontent.com/ktsaou/blocklist-ipsets/master/ri_connect_proxies_30d.ipset
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

init()
iteration_count=1
#subnet_update(1,2)
#init_ip(1)
#init_subnet(1,True)
compare_and_update(1,2)
while True:
	break
	download_files(iteration_count,True)
	subnet_init(1)
	break
	#Compares the previous and the present list and gets the difference
	old_ip,new_ip=compare_and_update(iteration_count-1,iteration_count)
	iteration_count=iteration_count+1
	file_to_write=open('logs','a')
	file_to_write.write(str(iteration_count)+","+str(old_ip)+","+str(new_ip)+"\n")
	file_to_write.close()
	break
