#!/usr/bin/python
#encoding:utf-8
""" Episode Finder implementation to go with video_finder_server.py"""

from gi.repository import GObject # pylint: disable=E0611

from twisted.internet import defer, reactor
import twisted.internet.protocol as protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint #point

from utils.messages import MessageEncoder

import logging
from logging import info, debug


class EpisodeFinderClientProtocol(NetstringReceiver):
	""" Twisted Protocol implementation """
	def __init__(self):
		self.encoder = MessageEncoder()
		self.defer = defer
		self.state = "init"
		self.defer_search_results = None
		self.defered_result_request_dl = None

	def stringReceived(self, string): #pylint: disable=C0103
		""" Data received protocol management
			Internal state dependant behavior :
			(init -> waiting results)
			(waiting results -> disconnect)
		"""
		result = self.encoder.decode(string)
		debug("receiving data")
		if self.state == "waiting_results" : 
			self.defer_search_results.callback(result)
			self.state = "waiting_dl_request"
		else:
			info("recieving result of dl launch order")
			self.defered_result_request_dl.callback(result) 
			info("finished : disconnecting")
			self.disconnect()

	def ep_request(self, episode):
		""" requests to deluge for @episode"""
		info("sending request to deluge")
		self.sendString(self.encoder.encode(episode))
		self.defer_search_results = defer.Deferred()
		self.state = "waiting_results"
		return self.defer_search_results

	def results_found(self):
		""" Unused method ? obsolete ?"""
		pass

	def dl_request(self, answer):
		""" Dl request handler -> 
		asks "answer" to be downloaded to the server

		returns the defered which will be triggered 
		when the server will have treated the request.
		"""
		logging.info("dl_request ...") 
		self.defered_result_request_dl = defer.Deferred()
		self.sendString(self.encoder.encode(answer))
		return self.defered_result_request_dl

	def disconnect(self):
		""" Disconnects """
		return self.transport.loseConnection()


class EpisodeFinderClientFactory(protocol.Factory):
	""" Factory for the client """	
	def __init__(self):
		pass
		#protocol.Factory.__init__(self)

	def buildProtocol(self, addr): #pylint: disable=C0103
		return EpisodeFinderClientProtocol()
from episode_video_finder import BaseEpisodeVideoFinder

class NetworkEpisodeVideoFinder(BaseEpisodeVideoFinder):
	""" Gobject encapsulation of Twisted Client"""
	def __init__(self):
		BaseEpisodeVideoFinder.__init__(self)
		self.episode = None 
		self.connected = False
		self.protoc = None

		self.got_results = None # defered end of request
		
		self.candidates = None # store for candidates
	# connection management callbacks

	def cleanup(self, res):
		""" Disconnects the twisted client """
		debug("result before cleanup :", res) 
		info("cleaning up ...")

		if self.connected: 
			return self.protoc.disconnect() 
		else: 
			return True

	def got_protocol(self, proto):
		""" Callback when connected
		launches the request,
		returns the defered which triggers when got the results
		"""
		info("\o/ got connection")
		def on_found(results):
			""" callback when results comes"""
			debug("emitting candidates found")
			self.emit("candidates_found") # pylint: disable=E1101
			debug(results)
			return results

		waiting_for_results = proto.ep_request(self.episode)\
				.addCallback(self._got_candidates)\
				.addCallback(on_found)
		self.set_protocol(proto)
		debug("protoq {}".format(self.protoc))
		self.connected = True
		return waiting_for_results 

	def set_protocol(self, protoc):
		""" protocol setter """
		self.protoc = protoc

	# API implementation

	def search_newep(self, episode):
		""" entry point """
		self.episode = episode
		info("searching newep {}...".format(episode))
		point = TCP4ClientEndpoint(reactor, "localhost", 8010)
		self.got_results = defer.Deferred()

  		# on connection launching request
		point.connect(EpisodeFinderClientFactory())\
				.addCallback(self.got_protocol)
		debug("adding callbacks for searching new eps")
		return self.got_results

	def _got_candidates(self, results):
		""" Callbacks when candidates arrives """
		self.candidates = results
		self.got_results.callback(results)
		return results

	def on_launched(self, res):
		""" Callback when dl launched"""
		self.emit("download_launched") # pylint: disable=E1101
		return res

	def on_chosen_launch_dl(self, chosen):
		""" Takes a choices, and launches the process
		returns a defered which triggers when dl is launched
		"""
		wait_for_launched_dl = self.protoc.dl_request(chosen)
		info("dl order launched for {}".format(chosen))
		return wait_for_launched_dl\
				.addCallback(self.on_launched)\
				.addBoth(self.cleanup) 

	
