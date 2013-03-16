#!/usr/bin/python
#encoding:utf-8
""" unittest fot torrent search servers and correcponding client
"""
import twisted
twisted.internet.base.DelayedCall.debug = True


from twisted.trial import unittest 
# import twisted.internet.protocol as protocol
from twisted.internet import reactor, defer
from twisted.internet.endpoints import TCP4ClientEndpoint

from datasource.video_finder_client import NetworkEpisodeVideoFinder, \
		EpisodeFinderClientFactory

import tests.common_test
from utils.on_event_deferred import OnEventDeferred #*

from logging import info
#class ServProcessProtocol(protocol.ProcessProtocol):
#	""" Dummy protocol for fake server, I guess"""
#	def __init__(self, deferred):
#		print "plop from process protocol"
#		self.defer = deferred
#	
#	def outReceived(self, data): #pylint: disable=C0103
#		print "Server outed :{}".format(data)
#		#self.defer.callback()
#		
#
#	def connectionMade(self):#pylint: disable=C0103
#		# self.defer.callback()
#		print "connection with child made"
#		print "plop"
		
class TestServer(unittest.TestCase):
	""" Test of launching a server """
	def setUp(self):#pylint: disable=C0103
		""" Init : 
		TODO: Launching a server automaticaly on init
		"""
		self.protoc = None
		# deferr = defer.Deferred()
		#self.serv_protocol = ServProcessProtocol(deferr)
		# reactor.spawnProcess(self.serv_protocol,\
			#"./video_finder_server.py",["./video_finder_server.py"])
		# subprocess.Popen("./video_finder_server")
		(self.serie, self.episode) = tests.common_test.get_serie_and_ep()
		#return deferr
		self.connected = None
		self.candidates = None

	def tearDown(self):#pylint: disable=C0103
		""" Nothing to do ?"""
		#try:
		#	self.serv_protocol.transport.signalProcess('TERM')
		#except Exception:
		#	pass
		pass


	def set_protocol(self, protoc):
		""" Callback : setter for protocol, needed for disconnection
		"""
		self.protoc = protoc
		info("setting protoc")

	def test_detailed(self):
		""" A simple test for creating a client,
		lots of details, design test
		"""
		deferred_results = defer.Deferred()
		self.connected = False
		
		deferred_launch = defer.Deferred()
		self.protoc = None
		#initial callback

		def got_protocol(protoc):
			""" Callback for connected """
			info("\n\o/ got connection")
			wait_for_connection = protoc.ep_request(self.episode)\
					.addCallback(got_results)
			self.set_protocol(protoc)
			self.connected = True
			return wait_for_connection


		def got_results(results):
			""" Callback : server answered """
			info("got results, res number : {}".format(len(results)))
			return deferred_results.callback(results)

		def choose(results):
			""" Choose a result from a results set"""
			info("choosing ...")
			return results[0]

		#def dl_launched(res):
		#	""" Callback """
		#	info("Dl_launched : {}".format(res))

		### After ###

		def end(results):
			""" End callback """
			info("OK ! results: {}".format(results))
			return True

		def cleanup(res):
			""" disconnect callback"""
			info("res : {}".format(res))
			info("cleaning up ...")
			if self.connected:
				return self.protoc.disconnect()
			else:
				return True
			
		def connection_error(res):
			""" Error connection callback """
			info("connection_error !!!!!!!")
			info("error: {}".format(res))
			deferred_results.errback(res)

		def request_res_from_dl(req):
			""" Callback : when chosen
			return a deferred which triggers when server answers
			"""
			info("sending final request")
			wait_for_dl_launch = self.protoc.dl_request(req)
			return wait_for_dl_launch.addCallback(deferred_launch.callback)

		# Creating client
		point = TCP4ClientEndpoint(reactor, "localhost", 8010)
		wait_for_connection = point.connect(EpisodeFinderClientFactory())
	
		# Connection, getting results
		wait_for_connection.addCallback(got_protocol).addErrback(connection_error) 
		# Choosing 
		deferred_results.addCallback(choose).addCallback(request_res_from_dl)
		# Ending 
		return deferred_launch.addCallback(end).addBoth(cleanup)

	def set_candidates(self, candidates):
		""" Candidates setter. Unused ? """	
		self.candidates = candidates

	def test_object_client(self):
		""" Testing the object client 'NetworkEpisodeVideoFinder'
		as a whole"""
		finder = NetworkEpisodeVideoFinder()
		finder.search_newep(self.episode)
		
		founded = OnEventDeferred(finder, "candidates_found")\
				.addCallback(self.set_candidates)
		def choose(res):
			""" Returns a candidate """
			info("res passed to choose :{}".format(res))
			return finder.candidates[0]

		def launch(choice):
			""" launches the dl"""
			return finder.on_chosen_launch_dl(choice)
		# defer.waitForDeferred(founded) # .addCallback(self.set_candidates)

		info("waiting for results ...")

		return founded.addCallback(choose).addCallback(launch)


	def test_search_and_choose(self):
		""" Whole process """
		ep_finder = NetworkEpisodeVideoFinder()
		def print_results(results):
			""" presentation callback"""
			#print("Résultats {}".format(len(results)))
			pass
		def catch_err(res):
			""" error callback """
			print "err catched {}".format(res)
		def choose(res):
			""" choose callback, actually launches a dl
			"""

			info("res {}".format(res))
			info( "Choosing {}".format(ep_finder.candidates[0]))
			
			ep_finder.on_chosen_launch_dl(ep_finder.candidates[0])
			info ("dl_launched ?")
			return True

		final_test = OnEventDeferred(ep_finder,"download_launched")
		final_test.add_error_event(ep_finder,"download_not_launched")

		candidates_found = OnEventDeferred(ep_finder, "candidates_found")\
				.addCallback(choose).addErrback(catch_err)
		
		ep_find = ep_finder.search_newep(self.episode)\
				.addCallback(print_results)
		return final_test.addBoth(catch_err) 

