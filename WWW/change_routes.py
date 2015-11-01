#!/usr/bin/env python
import base64
from joblib import Parallel,delayed
import time
import sys
import commands
from multiprocessing import Pool

#city=str(sys.argv[1])
#city=city[0].upper()+city[1:]
#ip=str(sys.argv[2])




#City , IP ,ASNto change



def change_route(*args):
	city=str(args[0][0])
	ip=str(args[0][1])
	asn=str(args[0][2])
	output= commands.getstatusoutput('python get_routes.py '+city+' '+ip)
	if "Item not in Table" in output[1]:
		return
		print "Route Cannot be Changed. Please try after sometime"	
	else:
		neighbor=output[1].strip().split(' ')[1]
		weight=int(output[1].strip().split(' ')[0]) + 1
		#Should be sent by the client // Takes more time to open the file everytime for a request
		#asn=7
		#file_to_read=open('asn_values','r')
		#for line in file_to_read:
		#	if city in line:
		#		asn=str(line.strip().split(',')[1])
		#		break
		output= commands.getstatusoutput('expect change_routes.exp '+city+' '+neighbor+' '+asn+' '+str(weight))
		print "Route has been changed"
		return








cities=sys.argv[1]
cities=base64.b64decode(cities)
cities=cities.replace('\\',' ')
cities=eval(cities)
processes = [(city,city_value['IP'],city_value['ASN']) for city,city_value in cities.iteritems()]
#print processes
start_time=time.time()
pool = Parallel(n_jobs=-1,pre_dispatch='all')
results = pool(delayed(change_route)(dd) for dd in processes)
end_time=time.time()
#print end_time-start_time
