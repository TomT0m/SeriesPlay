#! /usr/bin/python
#encoding:utf-8
""" Test communication with deluge """
from datasource.dl_manager import DelugeDlAdder
from twisted.trial import unittest # ,unittest.skip

# from unittest import skip # twisted.trial import unittest

from twisted.internet import reactor, defer
from deluge.ui.client import client

# for the fake RCPServer
import deluge.core.rpcserver
from deluge.core.rpcserver import RPCServer, log, \
		check_ssl_keys, ServerContextFactory
from deluge.core.rpcserver import Factory 
from deluge.core.core import Core
import deluge.component as component
import deluge.error
#import sys
# file extracted from deluge 
# http://git.deluge-torrent.org/deluge/tree/tests/common.py?h=deluge-1.3.5
import tests.deluge_common_tests as common 

import logging

__magnet_link__ = "magnet:?xt=urn:btih:038afcbf064655596d0500af2b74ebddf731bd5\
d&dn=Dirty+Sexy+Money+S02E07+The+Summer+House+HDTV+XviD-FQM+%5Beztv%5D&tr=udp%\
3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A\
80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80"

import twisted
twisted.internet.base.DelayedCall.debug = True

def rpc_clean_init(self, port=58846, interface="", \
		allow_remote=False, listen=True):
	""" temporary deluge initialisation replacement init """
	
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

	hostname = None
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
		self.port = reactor.listenSSL(port, \
				self.factory, ServerContextFactory(), interface=hostname)
	except Exception, exc:
		log.info("Daemon already running or port not available..")
		log.error(exc)

	
	#test for understanding how to clean

class DlManagerTester(unittest.TestCase):
	""" Tests communication with a fake deluge server """
	Port = 12321
	def setUp(self):
		""" init """
		common.set_tmp_config_dir()
		RPCServer.__init__ = rpc_clean_init
		self.rpcserver = RPCServer(listen = True, port = self.Port)
		self.core = Core()
		del_start = component.start()
		return del_start

	def tearDown(self):
		""" Shut down env """
		def on_shutdown(result):
			""" on server stopped"""
			logging.info(result)
			component._ComponentRegistry.components = {}
			
			del self.core
			del self.rpcserver
		
		wait_for_shutdown = defer.maybeDeferred(self.rpcserver.port.stopListening)
		defer.gatherResults([wait_for_shutdown])

		common.restore_config_dir()
		return component.shutdown().addCallback(on_shutdown)
	def test_empty(self):
		""" Init OK ? """
		pass

	def test_connect(self):
		""" Test client connection & cleanup with fake callback """
		plop = DelugeDlAdder(port=self.Port)
		return plop.connect().addCallback(plop.cleanup) #.addCallback()
	# unittest.@skip

	# @skip("do not understand what happens")
	def test_add_magnet(self):
		""" Test add a magnet, does not work ?? """
		plop = DelugeDlAdder(port=self.Port)
		return plop.add_magnet(__magnet_link__, ".").addBoth(plop.cleanup)
	# test_add_magnet.skip = "do not understand"
 
	def test_config_value(self):
		""" Test fake client by getting a conf value """
		plop = DelugeDlAdder(port=self.Port)
		wait_connection = plop.connect()
		wait_connection.addCallback(plop.on_connect_success).addCallback(plop.cleanup)
		return wait_connection
	
	
class TestServer(unittest.TestCase):
	""" Tests with a real deluge server """
	def test_1(self):
		""" Testcase : adding a magnet """
		plop = DelugeDlAdder(host="localhost")
		import os
		added = plop.add_magnet(__magnet_link__, \
				os.getcwd()).addCallback(plop.cleanup)
		return added

