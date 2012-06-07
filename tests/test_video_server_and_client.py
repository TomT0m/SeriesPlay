#!/usr/bin/python
#encoding:utf-8
import twisted
twisted.internet.base.DelayedCall.debug = True


from twisted.trial import unittest 
import twisted.internet.protocol as protocol
from twisted.internet import reactor
from twisted.internet.endpoints import *

from datasource.video_finder_client import *
import tests.common_test
from utils.on_event_deferred import *

class ServProcessProtocol(protocol.ProcessProtocol):
	def __init__(self,defer):
		print "plop from process protocol"
		self.defer = defer
	
	def outReceived(self,data):
		print "Server outed :{}".format(data)
		#self.defer.callback()
		

	def connectionMade(self):
		# self.defer.callback()
		print "connection with child made"
		print "plop"
		
class testServer(unittest.TestCase):
	def setUp(self):
		# deferr = defer.Deferred()
		#self.serv_protocol = ServProcessProtocol(deferr)
		# reactor.spawnProcess(self.serv_protocol,"./video_finder_server.py",["./video_finder_server.py"])
		# subprocess.Popen("./video_finder_server")
		(self.serie,self.episode) = tests.common_test.get_serie_and_ep()
		#return deferr
		pass
	def tearDown(self):
		#try:
		#	self.serv_protocol.transport.signalProcess('TERM')
		#except Exception:
		#	pass
		pass

	def emptyTest(self):
		print "bibou"
		pass
	def setProtocol(self,p):
		self.protoc=p
		print "setting protoc"

	def testSimple(self):
		deferred_results = defer.Deferred()
		self.connected = False
		
		deferred_launch = defer.Deferred()
		self.protoc = None
		#initial callback

		def got_protocol(p):
			print "\n\o/ got connection"
			d = p.ep_request(self.episode).addCallback(got_results)
			self.setProtocol(p)
			print "protoq {}".format(self.protoc)
			self.connected =True
			return d


		def got_results(results):
			print len(results)
			print "got results !!!"
			return deferred_results.callback(results)

		def choose(results):
			print "choosing ..."
			return results[0]

		def dl_launched(res):
			print res

		### After ###

		def end(results):
			print "OK !"
			return True

		def cleanup(res):
			print res
			print "cleaning up ..."
			if self.connected:
				return self.protoc.disconnect()
			else:
				return True
			
		def connection_error(res):
			print "connection_error !!!!!!!"
			print res
			deferred_results.errback(res)

		def request_res_from_dl(req):
			print "sending final request"
			defer = self.protoc.dl_request(req)
			print "bidou"
			return defer.addCallback(deferred_launch.callback)

		# Creating client
		point = TCP4ClientEndpoint(reactor,"localhost",8010)
		d = point.connect(EpisodeFinderClientFactory())
	
		# Connection, getting results
		d.addCallback(got_protocol).addErrback(connection_error) #.addCallback(got_results)
		# Choosing 
		deferred_results.addCallback(choose).addCallback(request_res_from_dl)
		# Ending 
		return deferred_launch.addCallback(end).addBoth(cleanup)

	def set_candidates(self,candidates):
		
		self.candidates = candidates

	def test_object_client(self):
		# def choose():
		#		self.candidates = None
		finder = network_episode_video_finder(self.episode)
		finder.search_newep(self.episode)
		self.res = None
		founded = OnEventDeferred(finder, "candidates_found").addCallback(self.set_candidates)
		def choose(res):
			return finder.candidates[0]
		def launch(choice):
			return finder.on_chosen_launch_dl(choice)
		# defer.waitForDeferred(founded) # .addCallback(self.set_candidates)

		print "looked like trigerred"

		return founded.addCallback(choose).addCallback(launch)


	def test_search_and_choose(self):
		ep_finder = network_episode_video_finder(self.episode)
		def print_results(results):
			print("Résultats {}".format(len(results)))
		def catch_err(res):
			print "err catched {}".format(res)
		def choose(res):
			print ep_finder.candidates[0]
			ep_finder.on_chosen_launch_dl(ep_finder.candidates[0])
			print "dl_launched ?" 
			return True

		final_test = OnEventDeferred(ep_finder,"download_launched")
		final_test.add_error_event(ep_finder,"download_not_launched")

		candidates_found = OnEventDeferred(ep_finder,"candidates_found").addCallback(choose).addErrback(catch_err)
		
		ep_find = ep_finder.search_newep(self.episode).addCallback(print_results)
		print "budou"	
		return final_test.addBoth(catch_err) # .addCallback(plop)#candidates_found.addCallback(final_test)# first_step.addCallback(final_test)

