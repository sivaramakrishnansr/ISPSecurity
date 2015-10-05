import getpass
import telnetlib
import sys
from optparse import OptionParser


HOST="localhost"
PORT="bgpd"
password="bgpuser"



parser=OptionParser()

parser.add_option("-d", "--destination", dest="destination", default='eth1',
            help="Router")

(options,args)=parser.parse_args()

destination=options.destination



tn=telnetlib.Telnet(HOST,PORT)
tn.read_until("Password: ")
tn.write(password+"\n")
data=''
data=tn.read_very_eager()

tn.write("sh ip bgp "+str(destination)+"\n")
data=''
data=tn.read_very_eager()
data=data.split('\n')

print data
