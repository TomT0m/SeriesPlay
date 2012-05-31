#!/usr/bin/python
#encoding:utf-8


from gi.repository import GObject

from twisted.internet import defer,reactor
import twisted.internet.protocol as protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.endpoints import *

from utils.messages import message_encoder



class EpisodeFinderClientProtocol(NetstringReceiver):
	def __init__(self):
		# Protocol.__init__(self)
		self.encoder = message_encoder()
		# self.ep_request()
		self.defer = defer

	def stringReceived(self,string):
		result = self.encoder.decode(string)
		print "receiving data"
		if self.state == "waiting_results" : 
			self.defer_search_results.callback(result)
			self.state="waiting_dl_request"
		else:
			print "recieving result of dl launch order"
			self.deferred_result_request_dl.callback(result) 
			print "finished"
			self.disconnect()

	def ep_request(self,ep):
		print "sending request"
		self.sendString(self.encoder.encode(ep))
		self.defer_search_results = defer.Deferred()
		self.state ="waiting_results"
		return self.defer_search_results

	def results_found(self):
		pass

	def dl_request(self,num):
		print "dl_request ..." 
		self.deferred_result_request_dl = defer.Deferred()
		self.sendString(self.encoder.encode(num))
		return self.deferred_result_request_dl

	def disconnect(self):
		return self.transport.loseConnection()


class EpisodeFinderClientFactory(protocol.Factory):
	def buildProtocol(self,addr):
		return EpisodeFinderClientProtocol()

class network_episode_video_finder(GObject.GObject):
        __gsignals__={ 
                'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
                'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
                'download_not_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),  
                'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())  
        }
	def __init__(self,episode):
		GObject.GObject.__init__(self)
		self.episode = episode
		self.connected = False

	# connection management callbacks

	def cleanup(self,res): 
		print res 
		print "cleaning up ..." 
		if self.connected: 
			return self.protoc.disconnect() 
		else: 
			return True
	def got_protocol(self,p):
		print "\n\o/ got connection"
		def on_found(results):
			print "emitting candidates found"
			self.emit("candidates_found")
			print results
			return results
		d = p.ep_request(self.episode).addCallback(self._got_candidates).addCallback(on_found)
		self.setProtocol(p)
		# print "protoq {}".format(self.protoc)
		self.connected =True
		# self.got_protocol.callback()
		return d 

        def setProtocol(self,p):
                self.protoc=p
                print "setting protoc"

	# API implementation

	def search_newep(self,ep):

		print "searching newep ..."
		point = TCP4ClientEndpoint(reactor,"localhost",8010)
		self.got_results = defer.Deferred()
  		# on connection launching request
                d = point.connect(EpisodeFinderClientFactory()).addCallback(self.got_protocol)
		print "adding callbacks for searching new eps"
		# d.addCallback(self.got_protocol) # .addCallback(self._got_candidates).addCallback(on_found)
		return self.got_results

	def _got_candidates(self,results):
		print "candidates ..."
		self.candidates=results
		self.got_results.callback(results)
		return results

	def on_launched(self,res):
		self.emit("download_launched")
		return res
	def on_chosen_launch_dl(self,chosen):
		#adder = dl_manager.deluge_dl_adder(host="localhost") 
		defer = self.protoc.dl_request(chosen)
		print "dl_launched"
		return defer.addCallback(self.on_launched).addBoth(self.cleanup) # adder.add_magnet(chosen.magnet,dl_path).addBoth(self.on_addition_success).addBoth(adder.cleanup)


# class 
def create_client():
	pass
	
