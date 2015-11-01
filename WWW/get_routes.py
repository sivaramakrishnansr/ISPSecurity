#!/usr/bin/env python

import sys
import commands
city=str(sys.argv[1])
city=city[0].upper()+city[1:]
#city="Munich"
#ip="165.0.0.0"
ip=str(sys.argv[2])
output= commands.getstatusoutput('expect get_routes.exp '+city+' '+ip)
ip_list=output[1].split('\n')
index_to_start=0
not_in_network=0
for item in ip_list:
	if "Network not in table" in item:
		print "Item not in Table"
		not_in_network=1
		break
	if "Advertised to non peer-group peers:" in item:
		index_to_start=ip_list.index(item)
		break


if not_in_network==0:
	ip_list=ip_list[index_to_start+2:-2]
	all_paths=[]
	line_count=0
	path=''
	for item in ip_list:
		if len(item)==1:
			continue
		line_count=line_count+1
		path=path+"\n"+item.strip()
		if line_count%4==0:
			all_paths.append(path)
			path=''

	path_details={}			
	path_count=0
	for item in all_paths:
		path_count=path_count+1
		item=item.split('\n')
		path_details[path_count]={}
		path_details[path_count]['Neighbor']=(item[2].split(' '))[0]
		weight=0
		if "weight" in item[3]:
			weight=int(((item[3].split('weight'))[1].strip()).split(',')[0])
		path_details[path_count]['Weight']=weight
		if "best" in item[3]:
			path_details[path_count]['Best']=True
		else:
			path_details[path_count]['Best']=False


	#Make it return the best weight and any other neighbor than the best
	best_weight=0
	alternate_neighbor=""
	for path,values in path_details.iteritems():
		if values['Best']==True:
			best_weight=int(values['Weight'])
			if len(path_details)!=1:
				continue
		alternate_neighbor=values['Neighbor']
	print best_weight,alternate_neighbor
			
else:
	print 0,0
