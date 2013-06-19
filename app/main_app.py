#!/usr/bin/python
#encoding:utf-8
""" Main App class definition module"""
# system imports
import os

import logging

#system libs

from gi.repository import Gtk #pylint: disable = E0611

#internal imports

from app.controller import ControllerModule, PlayEventManager

import ui.subtitles, ui.ui_utils, ui.videotorrent_list_control
from serie.fs_store import FsSeriesStore, FsManagedSeriesData
from serie.serie_manager import SeriesStore, SeriesData

from datasource.play_subdl import Subdownloader, TVsubtitlesSubdownloader\

from snakeguice.modules import Module

from app.config import Config
from app.service import PipeService, async_start

from twisted.internet import defer

class ControllerFactory(object):
	""" Factory creating a standard controller"""
	def create(self, app, series, injector):
		""" factory method"""
		return PlayEventManager(app, series, injector)
class VideoFinderService(object):
	pass

class AppModule(Module):
	""" snake guice application module configurator"""
	def configure(self, binder):
		""" binding definition """
		
		binder.bind(Subdownloader, to=TVsubtitlesSubdownloader)
		self.install(binder, ControllerModule())
		binder.bind(ControllerFactory, to=ControllerFactory)

		store = FsSeriesStore()
		config = Config()
		
		binder.bind(SeriesStore, to_instance = store)
		binder.bind(Config, to_instance = config)
		
		binder.bind(SeriesData, to = FsManagedSeriesData)
		binder.bind(VideoFinderService, 
	      		to_instance = PipeService("video_finder_server.py"))

class App(object):
	"""Class for main Manager app"""
	video_finder_key = "TorrentDl"
	
	def async_start_service(self, service, key):
		""" async start a service """
		async_start(service, self.services, key)

	def start_services(self):
		"""Add services used by app
		TODO: complete service
		"""
		# beginning of a Code Goldberg Machine
		# Keep it overly complex
		self.async_start_service(self.injector.get_instance(VideoFinderService),
						self.video_finder_key)

	def _get_service(self, key):
		return self.services[key]

	def get_service(self, key):
		""" Returns a MaybeDeferred which waits for service for starting 
		(if not started) to trigger its callback
		"""
		return defer.maybeDeferred(self._get_service, key)


	def stop_app(self, widg):
		""" Stop App 
		TODO : see if must move from event_mgr.end()"""
		self.stop()
		self.event_mgr.end(widg)
	
	def stop(self):
		""" Stop services """
		for serv in self.services.iterkeys():
			self.get_service(serv).addCallback(lambda serv: serv.stop())


	def __init__(self, injector):
		self.injector = injector

		store = injector.get_instance(SeriesStore) 
		config = injector.get_instance(Config)
		controller_factory = injector.get_instance(ControllerFactory)

		# Loading the main UI file
		gladefile = os.path.join(ui.ui_file)
		builder = Gtk.Builder()
		builder.add_from_file(gladefile)

		self.widg_tree = builder 
	
		self.services = {}

		self.start_services()

		# Model initialization
	
		self.store = store
		self.config = config

		#TODO: wtf ?
		# bash_factory = BashManagedSerieFactory(self.store)
		serie_list = self.store.get_serie_list()

		logging.info("creating serie manager")
		self.series = injector.get_instance(SeriesData) # bash_factory.create_serie_manager()
		logging.info("created serie manager")
	
		# View initialization : serie list combo

		serie_list.insert(0, self.series.current_serie.name)
		
		self.event_mgr = controller_factory.create(self, self.series, injector)
		ui.ui_utils.populate_combo_with_items(self.getitem("SerieListCombo"), \
				serie_list)
		
		# Control : data getter for serie initialization
		
		self.event_mgr.set_manager(self.store)
			
		# View : initial screen setup 
		

		# control : monitoring current season 
		# TODO: move to serie change control init
		self.event_mgr.put_monitor_on_saison()
	
		
		# Control initialization setting up callbacks 
		# on view alteration by user events

		dic = { "on_Play_clicked" : self.event_mgr.play,
			"on_SlaveMplayerPlay_clicked" : \
					self.event_mgr.play_windowed,
			"on_SerieListCombo_changed" : \
					self.event_mgr.selected_serie_changed,
			"on_MainWindow_destroy" : self.stop_app, \

			"on_numSaisonSpin_value_changed" : \
					self.event_mgr.update_season_number,
			"on_numEpSpin_value_changed" : self.event_mgr.update_episode_number,
			"on_skipTimeSpin_value_changed" : \
					self.event_mgr.update_skip_time,
			"on_decayTimeSpin_value_changed" : \
					self.event_mgr.update_decay_time,
			# "on_FPSComboBox_changed": self.event_mgr.update_fps,
			"on_CandidateSubsCombo_changed": \
					self.event_mgr.update_subtitle_file,
			"video_keypress": self.event_mgr.video_keypress,
			"on_SubtitlesTreeView_row_activated": \
					self.event_mgr.subtitle_seek ,
			"on_Synchro_Button_pressed": \
					self.event_mgr.subtitle_sync , 
			"on_SubtitlesTreeView_start_interactive_search" : \
					ui.subtitles.started_search,
			"on_OpenRep_clicked": \
					self.event_mgr.open_filemanager,
			"on_DlSub_clicked": \
					self.event_mgr.search_subtitles
			
		}

		self.window = self.widg_tree.get_object("MainWindow")
		self.widg_tree.connect_signals(dic)
		
		# Control : 
		# callback for quitting application on main window destroying installation
		
		if (self.window):
			self.window.connect("destroy", self.event_mgr.end )
		else:
			logging.info ("Pas trouvé")

	def getitem(self, key):
		""" Utility function, get a widget from is string ID """
		return self.widg_tree.get_object(key)

	season_number_spin_name = "numSaisonSpin"
	episode_number_spin_name = "numEpSpin"
	
	def selected_season(self):
		""" Getter : selected season number"""
		return self.getitem(self.season_number_spin_name).get_value()

	def selected_numep(self):
		""" Getter : selected episode number"""
		return self.getitem(self.episode_number_spin_name).get_value()

