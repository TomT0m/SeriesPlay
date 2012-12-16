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
from serie.bash_store import BashSeriesStore, BashManagedSerieFactory


from datasource.play_subdl import Subdownloader, TVsubtitlesSubdownloader\

from snakeguice import injector
from snakeguice.decorators import inject
from snakeguice.providers import create_instance_provider
from snakeguice.modules import Module

from app.config import Config


class ControllerFactory(object):
	""" Factory creating a standard controller"""
	def create(self, app, series):
		""" factory method"""
		return PlayEventManager(app, series)

class StoreProvider(object):
	def get(self):
		pass

class ConfigProvider(object): 
	def get(self):
		pass

class StdStoreProvider(object):
	def __init__(self, store):
		self.store = store
	def get(self):
		return store

class AppModule(Module):
	""" snake guice application module configurator"""
	def configure(self, binder):
		""" binding definition """
		
		binder.bind(Subdownloader, to=TVsubtitlesSubdownloader)
		self.install(binder, ControllerModule())
		binder.bind(ControllerFactory, to=ControllerFactory)

		store = create_instance_provider(BashSeriesStore())
		config = create_instance_provider(Config())
		
		binder.bind(store, to=StoreProvider)
		binder.bind(config, to=ConfigProvider)
		

class App(object):
	"""Class for main Manager app"""

	@inject(subdownloader = Subdownloader, 
	 controller_factory = ControllerFactory,
	 store_provider = StoreProvider,
	 config_provider = ConfigProvider )
	def __init__(self, subdownloader, controller_factory, store_provider, config_provider):

		# Loading the main UI file
		self.gladefile = os.path.join(ui.ui_file)
		builder = Gtk.Builder()
		builder.add_from_file(self.gladefile)

		self.widg_tree = builder 
		
		# Model initialization
	
		self.store = store_provider.get()
		self.config = config_provider.get()

		bash_factory = BashManagedSerieFactory(self.store)
		serie_list = self.store.get_serie_list()

		logging.info("creating serie manager")
		self.series = bash_factory.create_serie_manager()
		logging.info("created serie manager")
	
		# View initialization : serie list combo

		serie_list.insert(0, self.series.current_serie.name)
		
		#pylint: disable = E1101
		self.event_mgr = controller_factory.create(self, self.series)
		ui.ui_utils.populate_combo_with_items(self.getitem("SerieListCombo"), \
				serie_list)
		
		# Control : data getter for serie initialization
		
		subdl = subdownloader
		self.event_mgr.set_subdownloader(subdl)
		self.event_mgr.set_manager(self.store)
		
		# View : initial screen setup 
		

		# control : monitoring current season 
		# TODO: move to serie change control init
		self.event_mgr.put_monitor_on_saison()
	
		
		# Control initialization setting up callbacks 
		# on view alteration by user events

		dic = { "on_Play_clicked" : self.event_mgr.play,
			"on_SlaveMplayerPlay_clicked" : \
					self.event_mgr.play_with_sub,
			"on_SerieListCombo_changed" : \
					self.event_mgr.selected_serie_changed,
			"on_MainWindow_destroy" : self.event_mgr.end,
			"on_numSaisonSpin_value_changed" : \
					self.event_mgr.update_num_saison,
			"on_numEpSpin_value_changed" : self.event_mgr.update_num_episode,
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


