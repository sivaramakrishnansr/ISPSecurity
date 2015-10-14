import git
import MySQLdb
import os
import urllib2
import time
from time import mktime
from datetime import datetime
import calendar
password="kru!1ualahomora"
db=MySQLdb.connect(host="localhost",port=3306,user="root",passwd=password)
cur=db.cursor()

def get_list():
	list=[]
	file_to_read=open('list','r')
	for item in file_to_read:
		item=item.split('\t')
		item=item[0].strip()
		list.append(item)
	return list


def subnet_from_ip(ip):
	ip=ip.split('.')
	ip=ip[:-1]
	ip='.'.join(ip)
	ip=ip+".0/24"
	return ip


def subnet_insert(new_subnet_dict,new):
	if not new:
		insert_count=0
		for item in new_subnet_dict.iteritems():
			insert_count=insert_count+1
			subnet=item[0]
			count=str(item[1]['count'])
			start_time=str(item[1]['start_time'])
			if insert_count%10000==1:
				cmd='INSERT INTO SUBNET(ID,SUBNET,COUNT_HISTORY,START_TIME,ACTIVE,NUMBER_OF_APPEARANCE)VALUES(NOT NULL,\''+str(subnet)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
			else:
				cmd=cmd+","+'(NOT NULL,\''+str(subnet)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
			if insert_count%10000==0:
				cur.execute(cmd)
				db.commit()
				print "Done with",insert_count,"/",len(new_subnet_dict)
		if insert_count%10000!=0:
				cur.execute(cmd)
				db.commit()
	else:
		cmd=''
		insert_count=0
		for key,value in new_subnet_dict.iteritems():
			cur.execute('SELECT ID FROM SUBNET WHERE SUBNET=%s',str(key))
			if not cur.rowcount:
				insert_count=insert_count+1
				subnet=key
				count=str(value['count'])
				start_time=str(value['start_time'])
				if insert_count%10000==1:
					cmd='INSERT INTO SUBNET(ID,SUBNET,COUNT_HISTORY,START_TIME,ACTIVE,NUMBER_OF_APPEARANCE)VALUES(NOT NULL,\''+str(subnet)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
				else:
					cmd=cmd+","+'(NOT NULL,\''+str(subnet)+'\',\''+str(count)+'\',\''+str(start_time)+'\',1,0)'
				if insert_count%10000==0:
					cur.execute(cmd)
					db.commit()
					print "Done with",insert_count,"/",len(new_subnet_dict)
			else:
				for item in cur:
					cur.execute('UPDATE SUBSET SET START_TIME=%s,ACTIVE=1 WHERE ID=%s',(str(value['start_time']),str(item[0])))
					db.commit()
		if insert_count%10000!=0:
			cur.execute(cmd)
			db.commit()
	print "Added ",len(new_subnet_dict)


def subnet_remove(remove_dict):
	cmd=''
	remove_count=0
	end_time=int(calendar.timegm(time.gmtime()))
	for key,value in remove_dict.iteritems():
	 	cur.execute("SELECT ID,COUNT_HISTORY,START_TIME,DURATION,NUMBER_OF_APPEARANCE FROM SUBNET WHERE SUBNET=%s",(str(key)))
		for item in cur.fetchall():
			id=int(item[0])
			count_history=str(item[1])
			count_history=count_history+",0"
			start_time=int(item[2])
			duration=end_time-start_time
			duration_history=str(item[3])
			duration_history=duration_history+","+str(duration)
			number_of_appearance=int(item[4])+1
			active=0
			cur.execute('UPDATE SUBNET SET COUNT_HISTORY=%s, DURATION=%s,NUMBER_OF_APPEARANCE=%s,ACTIVE=0 WHERE ID=%s',(str(count_history),str(duration_history),str(number_of_appearance),str(id)))
			db.commit()
	print "Removed ",len(remove_dict)

def subnet_change(change_dict):
	cmd=''
	remove_count=0
	end_time=int(calendar.timegm(time.gmtime()))
	for key,value in change_dict.iteritems():
	 	cur.execute("SELECT ID,COUNT_HISTORY FROM SUBNET WHERE SUBNET=%s",(str(key)))
		for item in cur.fetchall():
			id=int(item[0])
			count_history=str(item[1])
			count_history=count_history+","+str(len(value['ip']))
			print id,count_history
			cur.execute('UPDATE SUBNET SET COUNT_HISTORY=%s WHERE ID=%s',(str(count_history),str(id)))
			db.commit()
	print "Changed ",len(change_dict)




def init_subnet(new_folder_name,update_db):
	cur.execute('USE SENSS')
	new_subnet_dict={}
	list=get_list()
	for file_name in list:
		if "set_file" in file_name:
			continue
		file_to_read=open(str(new_folder_name)+'/'+str(file_name),'r')
		for line in file_to_read:
			if "#" in line:
				if "Date:" in line:
					data=line.split('Date:')
					time_in_epoch=calendar.timegm(datetime.fromtimestamp(mktime(time.strptime(data[1].strip(),"%a %b  %d %H:%M:%S %Z %Y"))).timetuple())
				continue
			else:
				ip_address=line.strip()
				
				if "/" in ip_address:
						continue
				else:
					subnet=subnet_from_ip(ip_address)

				if subnet in new_subnet_dict:
					if ip_address not in new_subnet_dict[subnet]['ip']:
						new_subnet_dict[subnet]['count']=new_subnet_dict[subnet]['count']+1
						new_subnet_dict[subnet]['ip'].append(ip_address)
				else:
					new_subnet_dict[subnet]={}
					new_subnet_dict[subnet]['count']=1
					new_subnet_dict[subnet]['start_time']=time_in_epoch
					new_subnet_dict[subnet]['ip']=[]
					new_subnet_dict[subnet]['ip'].append(ip_address)

	if update_db:
		subnet_insert(new_subnet_dict)
	return new_subnet_dict


def subnet_update(old_folder_name,new_folder_name):
	cur.execute('USE SENSS')
	old_subnet_dict={}
	new_subnet_dict={}
	old_subnet_dict=init_subnet(old_folder_name,False)
	new_subnet_dict=init_subnet(new_folder_name,False)
	change=0
	added=0
	added_dict={}
	for key,value in new_subnet_dict.iteritems():
		if key not in old_subnet_dict:
			added=added+1
			added_dict[key]=value
	print "Added",added,len(added_dict)
	subnet_insert(added_dict,True)

	removed=0
	removed_dict={}
	changed_dict={}
	for key,value in old_subnet_dict.iteritems():
		if key in new_subnet_dict:
			if value['count']!=new_subnet_dict[key]['count']:
				changed_dict[key]=new_subnet_dict[key]
				change=change+1
		else:
			removed=removed+1
			removed_dict[key]=value

	print "Removed",removed,len(removed_dict)
	#subnet_remove(removed_dict)
	print "Changed",change
	#subnet_change(changed_dict)
	
	

