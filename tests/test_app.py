#!/usr/bin/python
#encoding: utf-8
""" Module testing Torrent List Controller """

from twisted.trial import unittest
import twisted 
from twisted.internet import reactor


from app.main_app import App
from app.controller import VideoFinderController, PlayEventManager, \
		ExternalPlayerHandler, get_combo_value
from app.config import Config


from tests.common_test import create_fake_env, MAIN_CONF_FILE

from serie.serie_manager import SeriesStore, SeriesData
from serie.fs_store import FsSeriesStore, FsManagedSeriesData


from datasource.play_subdl import EmptySubdownloader, Subdownloader
from snakeguice import Injector

from datasource.episode_video_finder import BaseEpisodeVideoFinder
import app.service

class DummyVideoFinder(BaseEpisodeVideoFinder):
	""" Testing class : do nothing """
	def add_video_finder(self, app, plop):
		""" dummy """
		pass

	def search_newep(self, epi):
		""" dummy too"""
		pass

class DummyPlayerHandler(object):
	""" Dummy """
	#pylint:disable=W0613
	def execute_play_command(self, controller, cmd, cwd = None):
		""" Justs waits then call end of play """
		reactor.callLater(0.1, controller.end_of_play)


from utils.factory import FactoryFactory
from snakeguice.modules import Module

class TestFinderModule(Module):
	""" Fake """
	def configure(self, binder):
		facto = FactoryFactory(DummyVideoFinder)
		binder.bind(FactoryFactory, to_instance = facto)

class FakeControllerModule(Module):
	""" Fake """
	def configure(self, binder):
		self.install(binder, TestFinderModule())
		binder.bind(VideoFinderController, to = VideoFinderController)
		binder.bind(ExternalPlayerHandler, to = DummyPlayerHandler)

class TestAppModule(Module):
	""" Test app module injection configuration"""
	def configure(self, binder):
		""" configure method"""
		binder.bind(Subdownloader, to=EmptySubdownloader)
		
		self.install(binder, FakeControllerModule())

		config = Config(MAIN_CONF_FILE)
		binder.bind(SeriesStore, to_instance = FsSeriesStore(MAIN_CONF_FILE))
		binder.bind(Config, to_instance = config)
		binder.bind(PlayEventManager, to = PlayEventManager)
		binder.bind(SeriesData, to = FsManagedSeriesData)
		binder.bind(VideoFinderService, to_instance = app.service.Service(None))

def create_app():
	""" Fake App factory function """
	inj = Injector(TestAppModule())

	return App(inj)


def value(combo):
	""" Returns selected combo box value """
	return combo.get_model().get_value(combo.get_active_iter(), 0)

def print_app_status(app):
	""" App info printing """
	combo_box = app.getitem("SerieListCombo")
	print("Série : {}, S{}E{}".format( value(combo_box), app.selected_season(), app.selected_numep()))

#pylint:disable=R0904
class TestVideotorrentController(unittest.TestCase):
	""" Controller testcase :
	* create app
	* empty selection
	* selection
	* cancelation
		"""
	#pylint: disable=C0103 
	def setUp(self): 
		""" setting up """
		twisted.internet.base.DelayedCall.debug = True
		print("setting up")

		create_fake_env('ZPlop', 2, 2)
		create_fake_env('Plop', 3, 2)
	
	def test_1(self):
		""" Fake app creation """
		app = create_app()
		print_app_status(app)

		combo_box = app.getitem("SerieListCombo")
		combo_box.set_active(0)
		print_app_status(app)
		self.assertTrue(value(combo_box) == 'Plop')

		season = app.selected_season()
		self.assertEquals(season, 3)
		ep = app.selected_numep()
		
		self.assertEquals(ep, 2)

		combo_box.set_active(2)
		print_app_status(app)
		
		self.assertEquals(value(combo_box), 'ZPlop')
		
		self.assertEquals((app.selected_season(), app.selected_numep()), (2, 2))

		app.stop()

		return 

	def test_change_serie(self):
		""" TestCase : change serie on ui """
		app = create_app()
		control = app.event_mgr

		print_app_status(app)
		
		control.update_serie_view()

		print_app_status(app)
		# combo_box = app.getitem("SerieListCombo")
		print_app_status(app)

		numep_widget = app.getitem("numEpSpin")

		numep_widget.set_value(3)
		
		self.assertEquals(app.selected_numep(), 3)	
		print_app_status(app)


		numsais_widget = app.getitem("numSaisonSpin")

		numsais_widget.set_value(8)
		print_app_status(app)

		self.assertEquals((app.selected_season(), app.selected_numep()), (8, 1))

		plop = get_combo_value(app.getitem("CandidateSubsCombo"))
		self.assertEquals(plop, None)

		app.stop()
