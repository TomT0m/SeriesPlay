#! /usr/bin/python -u
#encoding:utf-8

import pickle

from gi.repository import GObject

from twisted.internet import threads,defer
from twisted.internet.protocol import Factory,Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint,UNIXServerEndpoint
from twisted.protocols.basic import NetstringReceiver

import dl_manager
import play_tpb_search
from utils.messages import *
# import test_dl_manager

class episode_video_finder(GObject.GObject):
        __gsignals__={ 
                'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
                'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
                'download_not_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),  
                'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())  
        }
	def __init__(self,episode):
		GObject.GObject.__init__(self)
		self.episode = episode

	def search_newep(self,ep):
		def on_found(results):
			print "emitting candidates found"
			self.emit("candidates_found")
			print results
			return results

		finder = play_tpb_search.TPBMagnetFinder()
		d = threads.deferToThread(finder.get_candidates, ep.serie.nom,ep.num_saison,ep.num_ep )
		print "adding callbacks for searching new eps"		
		d.addCallback(self._got_candidates)
		d.addCallback(on_found)
		return d
	
	def _got_candidates(self,results):
		print "got candidates"
		self.candidates = results
		return results

	def on_addition_success(self,result=None):
		print "emitting download_launched" 
		self.emit("download_launched")

	def on_addition_fail(self,error):
		print "emitting addition_fail"
		print(error.exception_msg)
		self.emit("download_not_launched")
		return error

	def on_chosen_launch_dl(self,chosen):
		adder = dl_manager.deluge_dl_adder(host="localhost") 

		print "download link ?"	
		dl_path = self.episode.serie.get_path_to_season(self.episode.num_saison)
		print "dl_path : {}".format(dl_path)
		print "____________"

		return adder.add_magnet(chosen.magnet,dl_path).addBoth(self.on_addition_success).addBoth(adder.cleanup)

class EpisodeFinderServerFactory(Factory):
	def buildProtocol(self,addr):
		return EpisodeFinderServer()
	def doStart(self):
		print "started"
		import sys
		#sys.stdout.flush()
		print "flushed"

	def doStop(self):
		print "stopped !!"
	
class EpisodeFinderServer(NetstringReceiver):
	def __init__(self):
		print "building episode finder"
		self.state = "wait_episode"
		self.encoder = message_encoder()

	def doStart(self):
		print "started"
		import sys
		print "flushed"

	def doStop(self):
		print "stopped !!"
	
	def handle_ep_request(self,ep):
		def on_result_found(results):
			print "sending results"
			self.sendString(self.encoder.encode(results))
		def on_err(err):
			print "Erreur lors de l'ep request"
			print(err)
			return False

		self.episode_video_finder = episode_video_finder(ep)
		deferred = self.episode_video_finder.search_newep(ep)
		return deferred.addCallback(on_result_found).addErrback(on_err)

	def sendObject(self,obj):
		self.sendString(self.encoder.encode(obj))

	def handle_dl_request(self,message):
		def send_result(result):
			self.sendObject(result)
		print "dl_request ..."
		self.episode_video_finder.on_chosen_launch_dl(message).addCallback(send_result)

	def stringReceived(self,request):
		print "string received !!"
		#print "request : {}".format(request)
		
		request = self.encoder.decode(request)
		if self.state == "wait_episode":
			self.state = "wait_answer"
			self.handle_ep_request(request)
		else:
			self.handle_dl_request(request)

