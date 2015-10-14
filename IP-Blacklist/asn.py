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
cur.execute('USE SENSS')

def get_ip(folder_name):
	list=get_list()
	ip_list={}
	for file_name in list:
		if "set_file" in file_name:
			continue
		file_to_read=open(str(folder_name)+'/'+str(file_name),'r')
		for line in file_to_read:
			if "#" in line:
				if "Date:" in line:
					data=line.split('Date:')
					time_in_epoch=calendar.timegm(datetime.fromtimestamp(mktime(time.strptime(data[1].strip(),"%a %b  %d %H:%M:%S %Z %Y"))).timetuple())
					continue
			else:
				ip_address=line.strip()
				ip_list[ip_address]=time_in_epoch
	return ip_list

def write_input_file(file_name,write_list):
	file_to_write=open(file_name,'w')
	file_to_write.write("begin\n")
	for ip in write_list:
		file_to_write.write(ip+"\n")
	file_to_write.write("end\n")

def write_output(asn_dict):
	file_to_write=open('simple_output1','w')
	for key,value in asn_dict.iteritems():
		line_to_write=str(key)+","+str(value['count'])+","+str(value['name']+","+str(value['start_time'])+"\n")
		file_to_write.write(line_to_write)
	file_to_write.close()	

def difference(old_folder_name,new_folder_name):
	list=get_list()
	remove_ip={}
	add_ip={}
	for file_name in list:
		file_to_read=open(str(new_folder_name)+"/"+file_name,'r')
		for line in file_to_read:
			if "#" in line:
				if "Date:" in line:
					data=line.split('Date:')
					time_in_epoch=calendar.timegm(datetime.fromtimestamp(mktime(time.strptime(data[1].strip(),"%a %b  %d %H:%M:%S %Z %Y"))).timetuple())
				continue
		
		with open(str(old_folder_name)+"/"+file_name) as f:
			temp=[]
			for line in f:
				if '#' in line:
					continue
				temp.append(line.strip())
			t1s = set(temp)
		
		with open(str(new_folder_name)+'/'+file_name) as f:
			temp=[]
			for line in f:
				if '#' in line:
					continue
				temp.append(line.strip())
			t2s = set(temp)
		
		for diff in t1s-t2s:
			remove_ip[diff]=time_in_epoch

		for diff in t2s-t1s:
			add_ip[diff]=time_in_epoch
	return add_ip,remove_ip





def process_asn(output_file_name,asn_dict,ip_list):
	file_to_read=open(output_file_name,'r')
	cache_to_write=open('cache','a')
	na=0
	for line in file_to_read:
		if "Bulk mode; whois.cymru.com" in line:
			na=na+1
			continue
		original_line=line.split('|')
		as_number=original_line[0].strip()
		ip=original_line[1].strip()
		as_name=original_line[2].strip()
		if 'NA' in as_number and 'NA' in as_name:
			na=na+1
			continue
		cache_to_write.write(line)
		if ip in ip_list:	
			if as_number in asn_dict:
				asn_dict[as_number]['count']=asn_dict[as_number]['count']+1
			else:
				asn_dict[as_number]={}
				asn_dict[as_number]['name']=as_name
				asn_dict[as_number]['count']=1
				asn_dict[as_number]['start_time']=ip_list[ip]
	cache_to_write.close()
	print "Cache skip ",na

def update_cache(input_file_name,output_file_name,ip_list):
	count=0
	write_list=[]
	asn_dict={}
	for ip,start_time in ip_list.iteritems():
		count=count+1
		write_list.append(ip)
		if count%100000==0:
			print "Done with ",count,"/",len(ip_list)
			write_input_file(input_file_name,write_list)
			os.system('netcat whois.cymru.com 43 < '+input_file_name+' | sort -n > '+output_file_name)
			process_asn(output_file_name,asn_dict,ip_list)
			os.system('rm '+output_file_name)
			write_list=[]
	if len(write_list)!=0:
		write_input_file(input_file_name,write_list)
		os.system('netcat whois.cymru.com 43 < '+input_file_name+' | sort -n > '+output_file_name)
		process_asn(output_file_name,asn_dict,ip_list)
		os.system('rm '+output_file_name)
	return asn_dict	

def get_cache():
	cache_to_read=open('cache','r')
	cache={}
	for line in cache_to_read:
		line=line.split('|')
		as_number=line[0].strip()
		ip=line[1].strip()
		as_name=line[2].strip()
		cache[ip]=as_number
	return cache


def compare_and_update(old_folder_name,new_folder_name):
	add_ip,remove_ip=difference(old_folder_name,new_folder_name)
	cache=get_cache()
	ip_list={}
	print "Remove IP",len(remove_ip)
	print "Add IP",len(add_ip)
	for ip,start_time in add_ip.iteritems():
		if ip in cache:
			continue
		else:
			ip_list[ip]=start_time

	for ip,start_time in remove_ip.iteritems():
		if ip in cache:
			continue
		else:
			ip_list[ip]=start_time

	print "Updating Cache",len(ip_list)		
	update_cache('input','output',ip_list)
	cache=get_cache()
	update_add={}
	update_remove={}
	

	for ip,start_time in add_ip.iteritems():
		if ip in cache:
			if '/' in ip:
				ip=ip.split('/')
				ip=ip[0]
			if cache[ip] in update_add:
				update_add[cache[ip]]['count']=update_add[cache[ip]]['count']+1
				update_add[cache[ip]]['start_time']=start_time
			else:
				update_add[cache[ip]]={}
				update_add[cache[ip]]['count']=1
				update_add[cache[ip]]['start_time']=start_time

	for ip,start_time in remove_ip.iteritems():
		if ip in cache:
			if '/' in ip:
				ip=ip.split('/')
				ip=ip[0]
			if cache[ip] in update_remove:
				update_remove[cache[ip]]['count']=update_remove[cache[ip]]['count']+1
				update_remove[cache[ip]]['start_time']=start_time
			else:
				update_remove[cache[ip]]={}
				update_remove[cache[ip]]['count']=1
				update_remove[cache[ip]]['start_time']=start_time

	#Lets count the number of entries which we need to make
	return update_add,update_remove


def asn_insert(insert_db,check):
	if not check:
		insert_count=0
		for asn, value in insert_db.iteritems():
			count=value['count']
			start_time=value['start_time']
			insert_count=insert_count+1
			if insert_count%10000==1:
				cmd='INSERT INTO ASN(ID,ASN,COUNT_HISTORY,START_TIME,ACTIVE,NUMBER_OF_APPEARANCE)VALUES(NOT NULL,\''+str(asn)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
			else:
				cmd=cmd+","+'(NOT NULL,\''+str(asn)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
			if insert_count%10000==0:
				cur.execute(cmd)
				db.commit()
				print "Done with",insert_count,"/",len(insert_db)
		if insert_count%10000!=0:
				cur.execute(cmd)
				db.commit()
	else:
		for asn, value in insert_db.iteritems():
			cur.execute('SELECT ID,COUNT_HISTORY FROM ASN WHERE ASN=%s',(str(asn)))
			insert_count=0
			if not cur.rowcount:
				count=value['count']
				start_time=value['start_time']
				insert_count=insert_count+1
				if insert_count%10000==1:
					cmd='INSERT INTO ASN(ID,ASN,COUNT_HISTORY,START_TIME,ACTIVE,NUMBER_OF_APPEARANCE)VALUES(NOT NULL,\''+str(asn)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
				else:
					cmd=cmd+","+'(NOT NULL,\''+str(asn)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
				if insert_count%10000==0:
					cur.execute(cmd)
					db.commit()
			else:
				for item in cur:
					id=int(item[0])
					count_histroy_string=str(item[1])
					count_array=count_histroy_string.split(',')
					last_count=int(count_array[-1])
					count=last_count+int(value['count'])
					count_histroy_string=','.join(count_array)
					count_histroy_string=count_histroy_string+","+str(count)
					cmd="UPDATE ASN SET COUNT_HISTORY=\'"+count_histroy_string+"\' WHERE ID=\'"+str(id)+"\'"
					cur.execute(cmd)
					db.commit()	
					print "Made changes to ID",id
			if insert_count%10000!=0:
				cur.execute(cmd)
				db.commit()


def asn_delete(update_remove):
	for asn, value in update_remove.iteritems():
		cur.execute('SELECT ID,COUNT_HISTORY,NUMBER_OF_APPEARANCE FROM ASN WHERE ASN=%s',(str(asn)))
		insert_count=0
		if not cur.rowcount:
			continue
		else:
			for item in cur:
				id=int(item[0])
				count_histroy_string=str(item[1])
				count_array=count_histroy_string.split(',')
				last_count=int(count_array[-1])
				count=last_count-int(value['count'])
				count_histroy_string=','.join(count_array)
				count_histroy_string=count_histroy_string+","+str(count)
				if int(count)==0:
					active=0
					number_of_appearance=int(item[2])
					number_of_appearance=number_of_appearance+1
					cmd="UPDATE ASN SET COUNT_HISTORY=\'"+count_histroy_string+"\',NUMBER_OF_APPEARANCE=\'"+str(number_of_appearance)+"\',ACTIVE=0 WHERE ID=\'"+str(id)+"\'"
				else:
					cmd="UPDATE ASN SET COUNT_HISTORY=\'"+count_histroy_string+"\' WHERE ID=\'"+str(id)+"\'"
				cur.execute(cmd)
				db.commit()	
				print "Made changes to ID",id
		


def asn_init(folder_name):
	ip_list=get_ip(folder_name)
	cache=get_cache()
	ip_list_update={}
	for ip,start_time in ip_list.iteritems():
		if '/' in ip:
			ip=ip.split('/')
			ip=ip[0]
		if ip in cache:
			continue
		else:
			ip_list_update[ip]=start_time
	asn_dict=update_cache('input','output',ip_list_update)
	cache=get_cache()
	insert_db={}
	for ip,start_time in ip_list.iteritems():
		if ip in cache:
			if cache[ip] in insert_db:
				insert_db[cache[ip]]['count']=insert_db[cache[ip]]['count']+1
			else:
				insert_db[cache[ip]]={}
				insert_db[cache[ip]]['count']=1
				insert_db[cache[ip]]['start_time']=start_time
	asn_insert(insert_db,False)	
	return insert_db

#First Time Insert
insert_db=asn_init('1')

#Put this in the while loop
update_add,update_remove=compare_and_update('1','2')
asn_insert(update_add,True)
asn_delete(update_remove)
