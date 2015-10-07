import sys
import time
from ryu.base import app_manager
from ryu.controller import ofp_event, dpset
from ryu.controller.handler import MAIN_DISPATCHER,DEAD_DISPATCHER,CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub,ip
from ryu.ofproto import ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import MySQLdb

import itertools
class Controller(app_manager.RyuApp):

	
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    cur=0
    db=0
    id=0	
    def __init__(self, *args, **kwargs):
        global cur,db
	self.datapaths={}
        self.mac_to_port = {}
        host="root"
        password="kru!1ualahomora"
        db=MySQLdb.connect(host="localhost",port=3306,user=host,passwd=password)
        cur=db.cursor()
        cur.execute("USE SENSS")

	super(Controller, self).__init__(*args, **kwargs)
	
    @set_ev_cls(dpset.EventDP, MAIN_DISPATCHER)
    def switch_in(self, ev):
        dp  = ev.dp
        entered = ev.enter
	print "Got a connection from a switch",dp.id

    #Keeps track of all the switches which are entering and leaving the system	
    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER,DEAD_DISPATCHER])
    def _state_change_handler(self,ev):
		datapath=ev.datapath
		if ev.state == MAIN_DISPATCHER:
			if not datapath.id in self.datapaths:
				self.datapaths[datapath.id]=datapath
				self.monitor_thread=hub.spawn(self._monitor)

		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				del self.datapaths[datapath.id]

    #Thread which monitors the database for new requests	
    def _monitor(self):
                global cur,db,id 
		print "Thread Started"
		while True:
			if(len(self.datapaths)>0):
				break
		while True:
			db.commit()
			#Keep the ID to be 5
			cur.execute("SELECT ID FROM REQUEST WHERE COMPLETED=0 AND TYPE=1")
			rows=cur.fetchall()
			if rows:

				for item in rows:
					print item
					id=int(item[0])
			
				print "Got a request from the server",time.time(),id,rows
				
				
				for dp in self.datapaths.values():
					self._request_stats(dp)
				break
    #Generates a request stat message		
    def _request_stats(self,datapath):
		src_ip="10.1.2.2"
		#dst_ip="10.1.1.2"
		ofp=datapath.ofproto
		ofp_parser=datapath.ofproto_parser
		cookie=cookie_mask=0
		match =datapath.ofproto_parser.OFPMatch()
		dl_type = ether.ETH_TYPE_IP
		src_int=self.ipv4_to_int(src_ip)
		#dst_int=self.ipv4_to_int(dst_ip)
		match.set_dl_type(dl_type)
		#match.set_ipv4_src(src_int)
		#match.set_ipv4_dst(dst_int)
		req = ofp_parser.OFPFlowStatsRequest(datapath, 0,ofp.OFPTT_ALL,ofp.OFPP_ANY,ofp.OFPG_ANY,cookie, cookie_mask,match)
   		datapath.send_msg(req)
		print "Sent A Request"
    #Handles the stat request message
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply,MAIN_DISPATCHER)
    def flow_stats_reply_handler(self,ev):
		global cur,db,id
		body=ev.msg.body
		datapath=ev.msg.datapath.id
		#print datapath
		print "Got a Reply",body," this is it"
		cur.execute('UPDATE REQUEST SET COMPLETED=1 WHERE ID=%s',str(id))
		db.commit()		
		print "Sent an ACK to the server",time.time()

		for stat in body:
			print stat

    def ipv4_to_int(self, string):
        ip = string.split('.')
        assert len(ip) == 4
        i = 0
        for b in ip:
            b = int(b)
            i = (i << 8) | b
  	return i



    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)








