import getpass
import telnetlib
import sys
from optparse import OptionParser
import time

HOST="localhost"
PORT="bgpd"
password="en"
parser=OptionParser()
parser.add_option("-d", "--destination", dest="destination", default='eth1',
            help="Router")
(options,args)=parser.parse_args()
destination=options.destination
tn=telnetlib.Telnet(HOST,PORT)
data=tn.read_until("Password: ")
print data
tn.write(password+"\r\n")
data=''
data=tn.read_very_eager()
print data
tn.write("sh ip bgp "+str(destination)+"\r\n")
data=tn.read_some()
print data



#data=''
data=data+tn.read_very_eager()

print 
print
print
print data
data=data.split('\n')
neighbor=""
best_weight=0

for i in range(0,len(data)):
	if "best" in data[i]:
		metric_line=data[i].split(',')
		for item in metric_line:
			if "weight" in item:
				best_weight=item.split(' ')[2]
		continue
	
	if "Origin" in data[i]:
		neighbor=data[i-1]
		print neighbor
		neighbor=neighbor.strip().split(' ')[0]

print best_weight,neighbor
