#! /usr/bin/python
#encoding:utf-8

from datasource.dl_manager import *
from twisted.trial import unittest # ,unittest.skip

# from unittest import skip # twisted.trial import unittest

from twisted.internet import reactor,defer
from deluge.ui.client import client

# for the fake RCPServer
import deluge.core.rpcserver
from deluge.core.rpcserver import RPCServer,log,check_ssl_keys,ServerContextFactory
from deluge.core.rpcserver import Factory 
from deluge.core.core import Core
import deluge.component as component
import deluge.error
import sys
# file extracted from deluge http://git.deluge-torrent.org/deluge/tree/tests/common.py?h=deluge-1.3.5
import tests.deluge_common_tests as common 

magnet_link="magnet:?xt=urn:btih:038afcbf064655596d0500af2b74ebddf731bd5d&dn=Dirty+Sexy+Money+S02E07+The+Summer+House+HDTV+XviD-FQM+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80"

import twisted
twisted.internet.base.DelayedCall.debug = True

def RPC_CleanInit(self, port=58846, interface="", allow_remote=False, listen=True):
        component.Component.__init__(self, "RPCServer")

        self.factory = Factory()
        self.factory.protocol = deluge.core.rpcserver.DelugeRPCProtocol
        self.factory.session_id = -1
        # Holds the registered methods
        self.factory.methods = {}
        # Holds the session_ids and auth levels
        self.factory.authorized_sessions = {}
        # Holds the protocol objects with the session_id as key
        self.factory.session_protocols = {}
        # Holds the interested event list for the sessions
        self.factory.interested_events = {}


        if not listen:
            return

        if allow_remote:
            hostname = ""
        else:
            hostname = "localhost"

        if interface:
            hostname = interface

        log.info("Starting DelugeRPC server %s:%s", hostname, port)

        # Check for SSL keys and generate some if needed
        check_ssl_keys()

        try:
            self.port = reactor.listenSSL(port, self.factory, ServerContextFactory(), interface=hostname)
        except Exception, e:
            log.info("Daemon already running or port not available..")
            log.error(e)
            # sys.exit(0)
	
#test for understanding how to clean

class dl_manager_tester(unittest.TestCase):
	Port=12321
	def setUp(self):
        	common.set_tmp_config_dir()
		RPCServer.__init__=RPC_CleanInit
        	self.rpcserver = RPCServer(listen=True,port=self.Port)
        	self.core = Core()
        	d = component.start()
        	return d

        def tearDown(self):
		def on_shutdown(result):
            		component._ComponentRegistry.components = {}
			print("shutting down ---------------------------------------------------------")
			#print "---------------------{}================".format(self.rpcserver.port)
			#self.rpcserver.port.stopListening().gatherResults()
            		del self.core
            		del self.rpcserver
		
		d = defer.maybeDeferred(self.rpcserver.port.stopListening)
		defer.gatherResults([d])

        	common.restore_config_dir()
		return component.shutdown().addCallback(on_shutdown)
	def test_empty(self):
		pass

	def test_connect(self):
		plop=deluge_dl_adder(port=self.Port)
		return plop.connect().addCallback(plop.cleanup) #.addCallback()
	# unittest.@skip

	# @skip("do not understand what happens")
	def test_add_magnet(self):
		plop = deluge_dl_adder(port=self.Port)
		return plop.add_magnet(magnet_link,".").addBoth(plop.cleanup)
	test_add_magnet.skip="do not understand"
 
	def test_config_value(self):
		plop=deluge_dl_adder(port=self.Port)
		c = plop.connect()
		c.addCallback(plop.on_connect_success).addCallback(plop.cleanup)
		return c # plop.connect(port=self.Port).addCallback(plop.on_connect_success) #.addCallback(self.cleanup) #.addCallback()
	
	
class TestServer(unittest.TestCase):
	def test_1(self):
		plop=deluge_dl_adder(host="localhost")
		import os
		added = plop.add_magnet(magnet_link, os.getcwd()).addCallback(plop.cleanup) #.addErrback(plop.cleanup)
		return added

