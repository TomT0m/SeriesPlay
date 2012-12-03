#!/usr/bin/python
#encoding: utf-8
""" Module testing Torrent List Controler """

from twisted.trial import unittest
import twisted
# import ui
from gi.repository import Gtk #pylint: disable=E0611 

from ui.videotorrent_list_control import VideoFinderControler

from app.main_app import App
from app.controler import PlayEventManager

from tests.common_test import create_fake_env, MAIN_CONF_FILE

from serie.bash_store import BashSeriesManager, BashManagedSeriesData


from datasource.play_subdl import EmptySubdownloader, Subdownloader
from snakeguice import Injector

class ControllerFactory(object):
	def create(self, app, series):
		pass
class TestControllerFactory(object):
	""" Factory creating a standard controller"""
	def create(self, app, series):
		""" factory method"""
		return PlayEventManager(app, series)

class AppModule(object):
	""" snake guice application module configurator"""
	def configure(self, binder):
		""" binding definition """
		binder.bind(Subdownloader, to=EmptySubdownloader)
		#binder.bind(ControllerFactory, to=TestControllerFactory)


class FakeApp(object):
	""" Fake testing app 
	TODO: check for obsolescence"""
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


class TestAppModule(object):
	""" Test app module injection configuration"""
	def configure(self, binder):
		""" configure method"""
		binder.bind(Subdownloader, to=EmptySubdownloader)
		binder.bind(ControllerFactory, to=ControllerFactory)


def create_app():
	""" Fake App factory function """
	inj = Injector(TestAppModule())

	return inj.get_instance(App)

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

		create_fake_env('ZPlop', 2, 2)
		create_fake_env('Plop', 3, 2)

	def test_1(self):
		""" Fake app creation """
		app = create_app()
		# control = VideoFinderControler(app)
		combo_box = app.getitem("SerieListCombo")
		combo_box.set_active(2)
		return 

	def test_change_serie(self):
		""" TestCase : change serie on ui """
		app = create_app()
		
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		control = app.event_mgr
		
		# series = BashManagedSeriesData(bash_manager) #.current_serie
		# control = PlayEventManager(app, series)
		control.update_serie_view()

