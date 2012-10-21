#!/usr/bin/python
#encoding: utf-8
""" Module testing Torrent List Controler """

from twisted.trial import unittest
# import ui
from gi.repository import Gtk #pylint: disable=E0611 

from ui.videotorrent_list_control import VideoFinderControler

from app.main_app import App

class FakeApp(object):
	""" Fake testing app """
	def __init__(self):
		twisted.internet.base.DelayedCall.debug = True
		builder = Gtk.Builder()
		builder.add_from_file("../ui/IfacePlay.ui")

		self.window = builder.get_object("MainWindow")
		self.builder = builder
	
	def getitem(self, key):
		""" Utility function, get a widget from is string ID """
        	#return self.widg_tree.get_widget(key)
		return self.builder.get_object(key)

def create_app():
	""" Fake App factory function """
	return App()

class TestVideotorrentControler(unittest.TestCase):
	""" Controler testcase :
	* create app
	* empty selection
	* selection
	* cancelation
		"""
	def setUp(self): #pylint: disable=C0103
		""" setting up """
		print("setting up")

	def test_1(self):
		""" Fake app creation """
		app = create_app()
		control = VideoFinderControler(app)
		return control
	
