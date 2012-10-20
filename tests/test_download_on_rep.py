#! /usr/bin/python
#encoding: utf-8

from twisted.trial import unittest
from twisted.internet import defer # ,gtk2reactor as reactor
from gi.repository import GObject


from twisted.python.failure import Failure
from unittest import expectedFailure
# reactor.install()

import serie.serie_manager
from datasource.episode_video_finder import EpisodeVideoFinder
from utils.on_event_deferred import OnEventDeferred

import deluge.component as component
from deluge.log import setupLogger
setupLogger()

import tests.common_test

import sys,os

import logging

class gobj(GObject.GObject):
	__gsignals__={
		'ok' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
		'error' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,())
	}
	def __init__(self):
		GObject.GObject.__init__(self)


class testOnEventDeferred(unittest.TestCase):
	def testOK(self):
		obj = gobj()
		defe = OnEventDeferred(obj,"ok")
		obj.emit("ok")
		return defe # .maybeDeferred(defe)
		
#	@expectedFailure
	def testError(self): 
		obj = gobj()
		defe = OnEventDeferred(obj, "ok")
		defe.add_error_event(obj, "error")
		obj.emit("error")
		return defe.addCallbacks(self.fail, self.assertIsInstance, errbackArgs=(Failure,))
	def testCleanup(self):
		obj = gobj()
		defe = OnEventDeferred(obj, "ok")
		defe._clean()



class testDownloadOnRep(unittest.TestCase):
	__gsignals__={
		'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
		'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
		'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
	}
			
	def setUp(self):
		""" 
		TODO : Creating a fake environment
		"""
		
		# print("logging")
		logging.basicConfig(level=logging.DEBUG)
#		self.serie_manager = DummySeriesManager()
#		
#		self.serie = serie_manager.bashManagedSerie("Dexter",self.serie_manager)
#		self.episode = serie_manager.bashManagedEpisode(self.serie,5,1)
		(self.serie,self.episode) = tests.common_test.get_serie_and_ep()

		d = component.start()
		defer.gatherResults([d])
		try:
			os.makedirs(os.path.join(self.serie.get_path_to_serie(),'saison6'))
		except Exception:
			pass 
		return 

	def test_search(self):
		def print_results(results):
			print("Résultats {}".format(len(results)))
			return results
		ep_finder = EpisodeVideoFinder(self.episode)
		return ep_finder.search_newep(self.episode).addCallback(print_results)


	def test_search_for_ep(self):
		def print_results(results):
			print("Résultats {}".format(len(results)))
		ep_finder = EpisodeVideoFinder(self.episode)
		ep_find = ep_finder.search_newep(self.episode).addCallback(print_results)
		test = OnEventDeferred(ep_finder,"candidates_found")
		#defe = ep_find.search_newep(self.episode)
		return test.addCallback(self.assertTrue)

	def test_search_and_choose(self):
		ep_finder = EpisodeVideoFinder(self.episode)
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
		
		return final_test.addBoth(catch_err) # .addCallback(plop)#candidates_found.addCallback(final_test)# first_step.addCallback(final_test)
