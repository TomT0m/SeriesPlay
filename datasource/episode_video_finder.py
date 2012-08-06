#! /usr/bin/python -u
#encoding:utf-8
""" Datasource for file finding
"""

from gi.repository import GObject #pylint: disable=E0611

from twisted.internet import threads
from twisted.internet.protocol import Factory
from twisted.protocols.basic import NetstringReceiver

from logging import info, debug

from datasource import dl_manager
from datasource import play_tpb_search
from utils.messages import MessageEncoder

class EpisodeVideoFinder(GObject.GObject):
	""" 
	Gobject class for asynchronous video finding.
	emits signals when search is done

	"""
	__gsignals__ = { 
		'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
		'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
		'download_not_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),  
		'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())  
	}

	def __init__(self, episode):
		GObject.GObject.__init__(self)
		self.episode = episode
		self.candidates = None

	def search_newep(self, episode):
		"""Async method, 
		searches a magnet for a specified episode
		@episode : the searched episode

		returns a defered which trigers when the search is done
		"""
		def on_found(results):
			""" callback trigering when search is done"""
			debug("emitting candidates found")
			self.emit("candidates_found") #pylint: disable=E1101
			info("Résultats : {}".format(results))
			return results

		finder = play_tpb_search.TPBMagnetFinder()
		when_found = threads.deferToThread(finder.get_candidates, \
				episode.serie.nom, \
				episode.num_saison, \
				episode.num_ep)

		debug("adding callbacks for searching new eps")
		when_found.addCallback(self._got_candidates)
		when_found.addCallback(on_found)
		return when_found
	
	def _got_candidates(self, results):
		""" Triggers when results are done, 
		setter for candidates attribute """
		debug("got candidates")
		self.candidates = results
		return results

	def on_addition_success(self, result=None):
		""" callbacks when downloads launched """
		debug("emitting download_launched, result = {}".format(result)) 
		self.emit("download_launched") #pylint: disable=E1101

	def on_addition_fail(self, error):
		""" errback when download do not launched """
		debug("emitting addition_fail")
		info(error.exception_msg)
		self.emit("download_not_launched") #pylint: disable=E1101
		return error

	def on_chosen_launch_dl(self, chosen):
		""" callback chosen -> launching dl """
		adder = dl_manager.DelugeDlAdder(host="localhost") 

		info("download link ?")	
		dl_path = self.episode.serie.get_path_to_season(self.episode.num_saison)
		info("dl_path : {}".format(dl_path))
		info("____________")

		return adder.add_magnet(chosen.magnet, dl_path)\
				.addBoth(self.on_addition_success)\
				.addBoth(adder.cleanup)

class EpisodeFinderServerFactory(Factory):
	""" Trivial twisted Factory which builds a Episode finder
	"""
	def __init__(self):
		pass

	def buildProtocol(self, addr):  #pylint: disable=C0103
		return EpisodeFinderServer()

	def doStart(self): #pylint: disable=C0103
		info("starting ...")

	def doStop(self): #pylint: disable=C0103
		info("stopped !!")
	
class EpisodeFinderServer(NetstringReceiver):
	""" Server for finding magnets and handling requests
	(used in video_finder_server.py)
	"""
	def __init__(self):
		debug("building episode finder")
		self.state = "wait_episode"
		self.encoder = MessageEncoder()
		self.episode_video_finder = None

	def doStart(self): #pylint: disable=C0103
		""" nothing to do """
		info("server started")

	def doStop(self): #pylint: disable=C0103
		""" nothing to do """
		info("server stopped")
	
	def handle_ep_request(self, episode):
		""" Entry point method, calls to initiate a session
		@episode : the episode to search video for
		"""
		def on_result_found(results):
			""" Search done callback """
			info("sending video search results to client for {}...".format(episode))
			self.sendString(self.encoder.encode(results))

		def on_err(err):
			""" Error on search callback """
			info("Error on searching candidates video dowload for {}".format(episode))
			info(" ->: Err {}".format(err))
			return False

		self.episode_video_finder = EpisodeVideoFinder(episode)
		wait_for_result = self.episode_video_finder.search_newep(episode)
		return wait_for_result\
				.addCallback(on_result_found)\
				.addErrback(on_err)

	def sendObject(self, obj): #pylint: disable=C0103
		""" method for sending a python object instead of
		a string (extension of twisted string server)
		@obj : the object to send

		"""
		self.sendString(self.encoder.encode(obj))

	def handle_dl_request(self, message):
		""" server handler
		"""
		def send_result(result):
			""" callback for sending results to client"""
			self.sendObject(result)
		info("dl_request ...")
		self.episode_video_finder\
				.on_chosen_launch_dl(message)\
				.addCallback(send_result)

	def stringReceived(self, request): #pylint: disable=C0103
		""" Implementation of the twisted method
		analyses client request and modify internal state accordingly
		"""
		debug("string received !!")

		request = self.encoder.decode(request)
		if self.state == "wait_episode":
			self.state = "wait_answer"
			self.handle_ep_request(request)
		else:
			self.handle_dl_request(request)

