#!/usr/bin/python
#encoding: utf-8
""" Module testing Torrent List Controller """

from twisted.trial import unittest
# import ui
from gi.repository import Gtk #pylint: disable=E0611 
from ui.videotorrent_list_control import VideoFinderController

class FakeApp(object):
	""" Fake testing app """
	def __init__(self):
		builder = Gtk.Builder()
		builder.add_from_file("../ui/IfacePlay.ui")

		self.window = builder.get_object("MainWindow")
		self.builder = builder
	
	def getitem(self, key):
		""" Utility function, get a widget from is string ID """
        	#return self.widg_tree.get_widget(key)
		return self.builder.get_object(key)

	def stop(self):
		self.window.hide()

def create_app():
	""" Fake App factory function """
	return FakeApp()

class TestVideotorrentController(unittest.TestCase):
	""" Controller testcase :
	* create app
	* empty selection
	* selection
	* cancelation
	"""
	def setUp(self): #pylint: disable=C0103
		""" setting up """
		self.app = None
		print("setting up")

	def tearDown(self):
		self.app.stop()

	def test_1(self):
		""" Fake app creation """
		self.app = create_app()
		control = VideoFinderController(self.app)
		return control
	
