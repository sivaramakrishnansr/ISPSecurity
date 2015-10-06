import getpass
import telnetlib
import sys
from optparse import OptionParser
HOST="losangeles"
PORT="bgpd"
password="en"
parser=OptionParser()
parser.add_option("-n", "--neighbor", dest="neighbor", default='eth1',
            help="Neighbor")
parser.add_option("-w", "--weight", dest="weight", default='eth1',
            help="Weight")
parser.add_option("-r", "--router", dest="router", default='eth1',
            help="Router")
(options,args)=parser.parse_args()
#Neighbor Interface
neighbor=options.neighbor
#Changing the weight
weight=options.weight
#Router ID in the autonomous system .  Needed for quagga
router=options.router
tn=telnetlib.Telnet(HOST,PORT)
tn.read_until("Password: ")
tn.write(password+"\n")
data=''
data=tn.read_some()
tn.write("enable\n")
data=''
data=tn.read_some()
print data
tn.write(password+"\n")
data=''
data=tn.read_some()
print data
tn.write("config term\n")
data=''
data=tn.read_some()
print data
tn.write("router bgp "+router+"\n")
data=''
data=tn.read_some()
print data
tn.write("neighbor "+neighbor+" weight "+weight+"\n")
data=''
data=tn.read_some()
print data
tn.write("exit\n")
data=''
data=tn.read_some()
print data

tn.write("write\n")
data=''
data=tn.read_some()
print data

tn.write("exit\n")
data=''
data=tn.read_some()
print data

tn.write("clear ip bgp *\n")
data=''
data=tn.read_some()
print data


