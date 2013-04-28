#! /usr/bin/python
#encoding:utf-8
""" Unittesting UI
TODO : offscreen tests
"""

#import sys, os

from twisted.trial import unittest
from twisted.internet import defer, reactor
#from twisted.internet.task import Clock

from gi.repository import Gtk #pylint: disable=E0611

# from utils.on_event_deferred import OnEventDeferred
from ui.videotorrent_list_model import *

from logging import info

class Fresult:
	""" Fake result class """
	def __init__(self, torrent, link):
		self.magnet = link
		self.filename = torrent
		self.filesize = "Wow !"
		self.leechers = 90


def create_torrentlist():
	""" Fake data creation function 
	Returns a fake Torrent list with long names
	to fill the view
	"""
	name_str = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa {}'
	table = [Fresult(name_str.format(x),
		   'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb') 
		for x in range(100)]
	return table



class TestWindow(unittest.TestCase):
	""" Testing apparences """
	def setUp(self):
		""" Init : Gtk Builder needs to be"""
		builder = Gtk.Builder()
		builder.add_from_file("../ui/IfacePlay.ui")

		self.window = builder.get_object("MainWindow")
		self.builder = builder

	def tearDown(self):
		""" End of test """ 
		self.window.destroy()

	def test_init(self):
		""" Test the showing of widget"""
		builder = self.builder
		builder.add_from_file("../ui/IfacePlay.ui")

		window = builder.get_object("VideoSearchResultWindow")
		window.present()
		wait_timeout = defer.Deferred()
		def called():
			""" Timeout callback"""
			wait_timeout.callback(True)
		reactor.callLater(2, called) #pylint: disable=E1101

		return wait_timeout

	def test_populate(self):
		""" Test widget filled with fake content """
		builder = self.builder

		fakelist = create_torrentlist()
		store = VideoResultStore(fakelist)

		window = builder.get_object("VideoSearchResultWindow")
		window.present()
		info("window presented")
		view = builder.get_object("TorrentList")
		view.set_model(store.get_model())
		init_torrentlist_viewer(view)
		info("store inited")
		wait_timeout = defer.Deferred()
		def called():
			""" Timeout callback """
			wait_timeout.callback(True)
		reactor.callLater(2, called) #pylint: disable=E1101
		
		#ToClean:
			
		self.window.destroy()
		self.window = window
		
		return wait_timeout

class TestModel(unittest.TestCase):
	""" Testing Torrent Results model """
	def test_manipulating(self):
		""" Simple model manipulations """
		fakelist = create_torrentlist()
		store = VideoResultStore(fakelist)
		for content in store.get_model():
			info( "content of store : {} ".format(content))
		return self.assertTrue(True) # store.get_model().)

