#! /usr/bin/python
#encoding: utf-8

""" 
Testcases for torrent downloading integrated with interfaces
"""
from twisted.trial import unittest
from twisted.internet import defer 
from gi.repository import GObject


from twisted.python.failure import Failure
from unittest import expectedFailure

from datasource.episode_video_finder import EpisodeVideoFinder
from utils.on_event_deferred import OnEventDeferred

import deluge.component as component
from deluge.log import setupLogger
setupLogger()

import tests.common_test

import os

import logging

class Gobj(GObject.GObject):
	""" Fake GObject, just supposed to emit signals on demand"""
	__gsignals__ = {
		'ok' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
		'error' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,())
	}
	def __init__(self):
		GObject.GObject.__init__(self)


class TestOnEventDeferred(unittest.TestCase):
	""" Tests for OnEventDeferred object """
	def testOK(self):
		""" check if a deferred callbacks """
		obj = Gobj()
		defe = OnEventDeferred(obj,"ok")
		obj.emit("ok")
		return defe # .maybeDeferred(defe)
		
#	@expectedFailure
	def testError(self):
		""" checks if a deferred errbacks """

		obj = Gobj()
		defe = OnEventDeferred(obj, "ok")
		defe.add_error_event(obj, "error")
		obj.emit("error")
		return defe.addCallbacks(self.fail, 
			   self.assertIsInstance, 
			   errbackArgs=(Failure,))

	def testCleanup(self):
		""" Tests the if _clean method clears reactor """
		obj = Gobj()
		defe = OnEventDeferred(obj, "ok")
		defe._clean()



class TestDownloadOnRep(unittest.TestCase):
	""" Testcase : real downloading """
	__gsignals__ = {
		'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
		'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
		'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
	}
			
	def setUp(self):
		""" 
		TODO : Creating a fake environment
		"""
		
		logging.basicConfig(level=logging.DEBUG)
		(self.serie, self.episode) = tests.common_test.get_serie_and_ep()

		defe = component.start()
		defer.gatherResults([defe])
		try:
			os.makedirs(os.path.join(self.serie.get_path_to_serie(),'saison6'))
		except Exception:
			pass 
		return 

	def test_search(self):
		""" Printing results of an ep_finder """
		def print_results(results):
			""" simple printing method """ 
			#print("Résultats {}".format(len(results)))
			return results
		ep_finder = EpisodeVideoFinder()
		return ep_finder.search_newep(self.episode).addCallback(print_results)


	def test_search_for_ep(self):
		def print_results(results):
			#print("Résultats {}".format(len(results)))
			pass
		ep_finder = EpisodeVideoFinder()
		ep_find = ep_finder.search_newep(self.episode).addCallback(print_results)
		test = OnEventDeferred(ep_finder,"candidates_found")
		return test.addCallback(self.assertTrue)

	def test_search_and_choose(self):
		ep_finder = EpisodeVideoFinder()
		def print_results(results):
			pass
			#print("Résultats {}".format(len(results)))
		def catch_err(res):
			print "err catched {}".format(res)
		def choose(res):
			print ep_finder.candidates[0]
			ep_finder.on_chosen_launch_dl(ep_finder.candidates[0])
			print "dl_launched ?" 
			return True

		final_test = OnEventDeferred(ep_finder,"download_launched")
		final_test.add_error_event(ep_finder,"download_not_launched")

		candidates_found = OnEventDeferred(ep_finder,"candidates_found")\
				.addCallback(choose).addErrback(catch_err)
		ep_find = ep_finder.search_newep(self.episode).addCallback(print_results)
		
		return final_test.addBoth(catch_err) 
