#!/usr/bin/python
#encoding:utf-8


from gi.repository import GObject # pylint: disable=E0611

from twisted.internet import defer, reactor
import twisted.internet.protocol as protocol
from twisted.protocols.basic import NetstringReceiver
#from twisted.internet.endpoints import *
from twisted.internet.endpoints import TCP4ClientEndpoint #point

from utils.messages import message_encoder

import logging
from logging import info, debug


class EpisodeFinderClientProtocol(NetstringReceiver):
	def __init__(self):
		# Protocol.__init__(self)
		self.encoder = message_encoder()
		# self.ep_request()
		self.defer = defer
		self.state = "init"
		self.defer_search_results = None
		self.defered_result_request_dl = None

	def stringReceived(self, string):
		result = self.encoder.decode(string)
		print "receiving data"
		if self.state == "waiting_results" : 
			self.defer_search_results.callback(result)
			self.state = "waiting_dl_request"
		else:
			print "recieving result of dl launch order"
			self.defered_result_request_dl.callback(result) 
			print "finished"
			self.disconnect()

	def ep_request(self, episode):
		print "sending request"
		self.sendString(self.encoder.encode(episode))
		self.defer_search_results = defer.Deferred()
		self.state = "waiting_results"
		return self.defer_search_results

	def results_found(self):
		pass

	def dl_request(self, num):
		logging.info("dl_request ...") 
		self.defered_result_request_dl = defer.Deferred()
		self.sendString(self.encoder.encode(num))
		return self.defered_result_request_dl

	def disconnect(self):
		return self.transport.loseConnection()


class EpisodeFinderClientFactory(protocol.Factory):
	
	def __init__(self):
		pass
		#protocol.Factory.__init__(self)

	def buildProtocol(self, addr):
		return EpisodeFinderClientProtocol()

class network_episode_video_finder(GObject.GObject):
	__gsignals__ = { 
		'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
		'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
		'download_not_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),  
		'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())  
        }
	def __init__(self, episode):
		GObject.GObject.__init__(self)
		self.episode = episode
		self.connected = False
		self.protoc = None

		self.got_results = None # defered end of request
		
		self.candidates = None # store for candidates
	# connection management callbacks

	def cleanup(self, res): 
		print res 
		print "cleaning up ..." 
		if self.connected: 
			return self.protoc.disconnect() 
		else: 
			return True
	def got_protocol(self, proto):
		logging.info("\n\o/ got connection")
		def on_found(results):
			debug("emitting candidates found")
			self.emit("candidates_found") # pylint: disable=E1101
			print results
			return results
		defe = proto.ep_request(self.episode)\
				.addCallback(self._got_candidates)\
				.addCallback(on_found)
		self.set_protocol(proto)
		debug("protoq {}".format(self.protoc))
		self.connected = True
		# self.got_protocol.callback()
		return defe 

	def set_protocol(self, protoc):
		self.protoc = protoc

	# API implementation

	def search_newep(self, ep):
		info("searching newep {}...".format(ep))
		point = TCP4ClientEndpoint(reactor, "localhost", 8010)
		self.got_results = defer.Deferred()

  		# on connection launching request
		defe = point.connect(EpisodeFinderClientFactory())\
				.addCallback(self.got_protocol)
		debug("adding callbacks for searching new eps")
		# d.addCallback(self.got_protocol) 
		# .addCallback(self._got_candidates).addCallback(on_found)
		return self.got_results

	def _got_candidates(self, results):
		print "candidates ..."
		self.candidates = results
		self.got_results.callback(results)
		return results

	def on_launched(self, res):
		self.emit("download_launched") # pylint: disable=E1101
		return res

	def on_chosen_launch_dl(self, chosen):
		defe = self.protoc.dl_request(chosen)
		info("dl_launched")
		return defe.addCallback(self.on_launched).addBoth(self.cleanup) 
		# adder.add_magnet(chosen.magnet,dl_path)\
				#.addBoth(self.on_addition_success).addBoth(adder.cleanup)


# class 
def create_client():
	pass
	
