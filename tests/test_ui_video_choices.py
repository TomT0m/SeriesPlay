#! /usr/bin/python
#encoding:utf-8

import sys,os

from twisted.trial import unittest
from twisted.internet import defer,reactor
from twisted.internet.task import Clock

from gi.repository import GObject,Gtk

from utils.on_event_deferred import OnEventDeferred
from ui.videotorrent_list_model import *

class result:
	def __init__(self,torrent,link):
		self.magnet = link
		self.filename = torrent
		self.filesize= "Wow !"
		self.leechers=90


def create_torrentlist():
	table=[result('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa {}'.format(x),'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb') for x in range(100)]
	return table



class test_window(unittest.TestCase):
	def setUp(self):
		builder = Gtk.Builder()
		builder.add_from_file("../ui/IfacePlay.ui")

		self.window = builder.get_object("MainWindow")
		self.builder = builder

	def tearDown(self):
		self.window.destroy()

	def test_init(self):
		builder = self.builder
		# print os.getcwd()
		builder.add_from_file("../ui/IfacePlay.ui")

		window = builder.get_object("VideoSearchResultWindow")
		window.present()
		deferred = defer.Deferred()
		# deferred.addCallback(lambda x:True)
		def end(res):
			print "End"
			return res
		def called():
			deferred.callback(True)
			print "plop !!!"
		reactor.callLater(2,called)

		print "plop"
		return deferred

	def test_populate(self):
		builder = self.builder

		fakelist = create_torrentlist()
		store = video_result_store(fakelist)

		window = builder.get_object("VideoSearchResultWindow")
		window.present()
		print "presented"
		view = builder.get_object("TorrentList")
		view.set_model(store.get_model())
		init_torrentlist_viewer(view)
		print "inited"
		deferred = defer.Deferred()
		def called():
			deferred.callback(True)
			print "plop !!!"
		reactor.callLater(2,called)

		
		return deferred
	#test_populate.skip="investigating Segfault"

class test_model(unittest.TestCase):
	def test_manipulating(self):
		fakelist = create_torrentlist()
		store = video_result_store(fakelist)
		for x in store.get_model():
			print "x : {} ".format(x)
		return self.assertTrue(True) # store.get_model().)
