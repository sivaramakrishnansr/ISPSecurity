#!/usr/bin/env python
import threading
from joblib import Parallel,delayed
from multiprocessing import Pool
import sys
import time
import socket
import time
import ssl
import threading
import getpass
import telnetlib
import getpass
import telnetlib
import itertools
import urllib2
import time
import json


switch_list=[]
get_route_result={}
change_route_timestamp={}
get_route_timestamp={}
BASE_URL="http://localhost:8080/"


def store_switch_list():
	global switch_list
	URL=url_constructor("switch_list")
	req=urllib2.Request(URL)
	res = urllib2.urlopen(req)
	list= res.read()
	switch_list=eval(list)

def url_constructor(type,switch_id=0):
	global BASE_URL
	if type=="switch_list":
		URL=""
		URL=BASE_URL+"stats/switches"
	if type=="get_stats":
		URL=""
		URL=BASE_URL+"stats/aggregateflow/"+str(switch_id)
	if type=="add_flow":
		URL=""
		URL=BASE_URL+"stats/flowentry/add"
	return URL



def OFPMatch_Generator(match_dict):
        OFPMatch={}
        OFPMatch={}
        for key,value in match_dict.iteritems():
                OFPMatch[key]=value
        return OFPMatch

def OFPAction_Generator(action_dict):
	return [{"type":"OUTPUT","port":action_dict["port"]}]


def Addflow_Generator(dpid,match_dict,action_dict):
        OFPMatch=OFPMatch_Generator(match_dict)
	OFPAction=OFPAction_Generator(action_dict)
	addflow_construct={}
	addflow_construct["dpid"]=int(dpid)
	addflow_construct["priority"]=22220
	addflow_construct["match"]=OFPMatch
	addflow_construct["actions"]=OFPAction
	return addflow_construct


def add_flow(match_dict,action_dict,start_time):
	global switch_list
	dpid=switch_list[3]
	URL=url_constructor("add_flow",dpid)
	addflow_construct=Addflow_Generator(dpid,match_dict,action_dict)
        req=urllib2.Request(URL,json.dumps(addflow_construct))
        res = urllib2.urlopen(req)
	response={}
	response['Status']='OK'
	print str(response)

store_switch_list()
match_dict={"in_port":89}
action_dict={"port":1}
start_time=time.time()
add_flow(match_dict,action_dict,start_time)

