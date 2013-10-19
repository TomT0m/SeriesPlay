#! /usr/bin/python
#encoding: utf-8
""" Main App controller : 
	* callback functions """

# system imports
import os
import subprocess
import threading

import logging


from gi.repository import GObject #pylint: disable = E0611
from gi.repository import Gtk #pylint: disable = E0611
from gi.repository import Gio #pylint: disable = E0611



from twisted.internet import reactor

#internal imports

from gobj_player.gobj_player import PlayerStatus
from datasource.play_subdl import \
	thr_sub_dl
from datasource.play_subdl import Subdownloader
from datasource.video_finder_client import NetworkEpisodeVideoFinder

import ui.subtitles, ui.ui_utils, ui.videotorrent_list_control
from ui.videotorrent_list_control import VideoFinderController

from utils.cli import CommandExecuter, CommandLineGenerator

from serie.serie_manager import Episode
from snakeguice.modules import Module

from app.serie_controller import SeriesController

from utils.factory import FactoryFactory

class ControllerFactory(object):
	""" Factory creating a standard controller"""
	def create(self, app, series, injector):
		""" factory method"""
		return PlayEventManager(app, series, injector)
	def create_series_control(self, list_combo, series, injector):
		""" method to build the Glib series controller """
		return SeriesController(list_combo, series, injector)


class ExternalPlayerHandler(object):
	""" Interface for external player handling 

	behavior:
	supposed to call controller.end_of_play() at end of playing
	
	TODO: replace with a cleaner version that takes an episode object as parameter
	"""
	def execute_play_command(self, controller, cmd, cwd = None):
		""" Method to call to launch player """
		raise NotImplementedError("Interface")
	
class StdExternalPlayerHandler(object):
	""" Implementation with legacy bash script """
	def __init__(self):
		self.controller = None
		self.handle_file = None
		self.handle_end = None
		self.current_process = None

	def execute_play_command(self, controller, cmd, cwd = None):
		""" Launches cmd command
		and install monitors for finding when it stops and
		when it outputs to avoid UI hangouts
		"""
		
		self.controller = controller
		logging.debug("executing ... >>>{0}<<<".format(cmd))
		process = subprocess.Popen(cmd, \
				shell = False, bufsize = 0, stdout = subprocess.PIPE, cwd = cwd)
		self.current_process = process.stdout
		logging.debug("launched")
		
		self.handle_file = GObject.io_add_watch(
				self.current_process, GObject.IO_HUP, 
				self.end_of_play, priority = GObject.PRIORITY_DEFAULT_IDLE)
		self.handle_end = GObject.io_add_watch(
				self.current_process, GObject.IO_IN, 
				self.read, priority = GObject.PRIORITY_DEFAULT_IDLE)
		self.current_process = process

		return True

	def end_of_play(self, widg, condition = None):#pylint: disable=W0613
		""" Callbacks called when the MPlayer process stops
		Action : reactivates buttons, 
		launches UI updates for next episode, update models
		"""
		logging.info("end of play !")
		
		self.current_process = None
		GObject.source_remove(self.handle_file)
		GObject.source_remove(self.handle_end)

		self.controller.end_of_play()

		return False	

	def read(self, widg, condition):#pylint: disable=W0613
		""" Eats line from Mplayer process"""
		if self.current_process != None :
			self.current_process.stdout.read(1000)
			if self.current_process.poll() != None :
				pass
			return True
		else :
			logging.debug("callback deletion")
			return False


class VideoFinderModule(Module):
	""" Module : binding a NetworkEpisodeVideoFinder """
	def configure(self, binder):
		""" Module setup """
		facto = FactoryFactory(NetworkEpisodeVideoFinder)
		binder.bind(FactoryFactory, to_instance = facto)

class ControllerModule(Module):
	""" Controller module binder"""
	def configure(self, binder):
		""" Binding congiguration : 
			* VideoFinderController Needed"""
		self.install(binder, VideoFinderModule())
		binder.bind(VideoFinderController, to = VideoFinderController)
		binder.bind(ExternalPlayerHandler, to = StdExternalPlayerHandler)


def get_combo_value(combo):
	itera = combo.get_active_iter()
	if not itera:
		return None
	return combo.get_model().get_value(itera, 0)

class PlayEventManager(object):
	""" Class regrouping l callbacks and
	data updating functions
	"""

	def __init__(self, iface, serie_model, injector):
		self.app = iface
		self.current_process = None
		self.injector = injector
		
		# injected classes
		self.player_handler = injector.get_instance(ExternalPlayerHandler)
		self.video_finder_controller = injector.get_instance(VideoFinderController)
		
		logging.debug ("creating event manager")
		
		self.play_buttons = ["Play", "SlaveMplayerPlay", "DlSub", "OpenRep"]
		self.serie_model = serie_model

		logging.debug ("Setting up file monitoring ... ")
		nomfic = serie_model.get_base_path()
		fichier = Gio.File.new_for_path(nomfic)
		if(fichier):
			self.monitor = fichier.monitor_directory(Gio.FileMonitorFlags.NONE, None)
			self.monitor.connect("changed", self.update_serie_list)
		self.player_status = PlayerStatus()


		## subtitle view init
		cellpb = Gtk.CellRendererText()
		cellpbtext = Gtk.CellRendererText()
		time = Gtk.TreeViewColumn("Début", cellpb)
		time.set_cell_data_func(cellpb, ui.subtitles.subtitle_begin_time_getter)

		column = Gtk.TreeViewColumn("Sous-Titre", cellpbtext, text =1)

		column.set_cell_data_func(cellpbtext, ui.subtitles.subtitle_line_text_getter)

		sub_treeview = self.app.getitem("SubtitlesTreeView")
		sub_treeview.append_column(time)
		sub_treeview.append_column(column)

		sub_treeview.set_enable_search(True)
		sub_treeview.set_search_column(1) # num_trad_column-1)
		sub_treeview.set_search_equal_func(\
				ui.subtitles.subtitle_comparison_function, "")

		# init of video finder window
		ui.videotorrent_list_model\
				.init_torrentlist_viewer(\
				self.app.getitem("TorrentList"))

		## MPlayer subwindow		

# self.MPlayer = mplayer_slave.player(self.\
		#iface.getitem("VideoZone").window.xid)
# self.MPlayer = mplayer_slave.player(None) 
# self.MPlayer = mplayer_slave.player(None) 
# self.app.getitem("VideoZone").window.xid)
# logging.info ("XID :", self.app.getitem("VideoZone").window.xid)
# self.payer_status = None

		# Gio File watching handles
		self.handle_file = None
		self.handle_end = None
		self.subtitle_downloader = injector.get_instance(Subdownloader)
		self.monitor_serie = None # making an attribute to prevent gc
		self.manager = None

		factory = injector.get_instance(ControllerFactory)
		self.series_constroller = factory.create_series_control(self.app.getitem("SerieListCombo"), serie_model, injector)

		self.update_serie_view()

	def update_serie_list(self, 
			monitor, fichier, data, event): #pylint: disable=W0613
		""" Callbacks when a new file is added in the Serie directory,
		Action : updates the Serie Combo
		"""
		logging.info("Recherche d'une nouvelle série")
		model = self.app.getitem("SerieListCombo").get_model()
		serie_list = self.manager.get_serie_list()
		
		new_items = [x for x in serie_list if not self.serie_model.series.has_key(x) ]
		
		for new_serie in new_items:
			self.serie_model.add_serie(new_serie)
			model.append([new_serie])
		
	def update_subs_and_file(self, monitor, fichier, data, event):\
			#pylint: disable=W0613
		""" Callbacks when a new file is added on the Season directory
		Action : calls update_serie
		"""
		logging.info("Recherche d'un nouveau sub / vidéo ?")
		if ( event == Gio.FileMonitorEvent.CREATED ):
			self.update_episode_view()

	def open_filemanager(self, widg):#pylint: disable=W0613
		""" Opens a Nautilus Window on current season directory"""
		command_launch = CommandExecuter()
		command_gen = CommandLineGenerator("xdg-open")
		rep = self.serie_model.get_current_serie().get_path_to_current_season()
		command_gen.add_option_single(rep)
		command_launch.get_output(command_gen.get_command())
		
	def play(self, widg):#pylint: disable=W0613
		""" Callback when a play is requested
		** Unused currently **, probably obsolete
		Action : Launches 'play' script with current episode parameters"""
		logging.info("playing ... " + self.serie_model.get_current_serie().name)
		if self.current_process == None :
			serie = self.serie_model.get_current_serie()
			
			command = CommandLineGenerator("serie_next")
			chemin_serie = self.serie_model.get_current_serie().get_path_to_serie()
			
			epi = serie.season.episode

			command.add_option_param("-s", unicode(serie.season.number))
			command.add_option_param("-e", unicode(epi.number))
			command.add_option_param("-G", unicode(serie.get_skip_time()))
			fps = serie.get_fps()
			if fps:
				command.add_option_param("-f", unicode(fps))
			command.add_option_param("-d", unicode(serie.get_decay_time()))
			
			subfile = get_combo_value(self.app.getitem("CandidateSubsCombo"))
			if subfile:
				command.add_option_param("-t", subfile)
			
			vidfile = self.app.getitem("NomficLabel").get_text()
			if vidfile:
				command.add_option_param("-v", vidfile)
			
			#TODO: replace this legacy code

			os.environ["SEASON"] = self.serie_model.current_serie.name
			
			self.player_handler.execute_play_command(self, command.get_command(), cwd = chemin_serie)
	
	def end_of_play(self, widg = None, condition = None):#pylint: disable=W0613
		""" Callbacks called when the MPlayer process stops
		Action : reactivates buttons, 
		launches UI updates for next episode, update models
		"""
		logging.info("end of play !")
		for nom in self.play_buttons :
			self.app.getitem(nom).set_sensitive(True)
		self.current_process = None
		if not self.app.getitem("SetupModeCheck").get_active():
			self.serie_model.current_serie.on_seen_episode()
			self.update_serie_view()
		return False	
	
	def play_windowed(self, widg):#pylint: disable=W0613
		""" Callback when button is clicked
		Actions
		* Launches MPlayer, in a window,
		* sets UI in playing mode
		* installs end of play callbacks
		"""

		#if self.current_process == None :
		#	self.execute_play_command(["series","-S"])
		logging.info("playing in a slave MPlayer !!")
#if self.MPlayer == None:
	# self.MPlayer = mplayer_slave.player(\
	#		self.app.getitem("VideoZone").window.xid)
#	self.MPlayer = mplayer_slave.player() 
	#self.app.getitem("VideoZone").window.xid)
#	pass
# else:
		serie = self.serie_model.current_serie
		vid_list = serie.season.episode.get_video_list()
		
		filename = None
		if len(vid_list) > 0:
			filename = serie.get_absolute_filename(vid_list[0])
		
		path = serie.get_path_to_current_season()
		
		
		sublist = serie.season.episode.get_subtitle_list()
		
		if len(sublist) > 0 :
			subfile = sublist[0]
		else:
			sublist = None
		
		if filename != None :
			self.player_status.play(filename)
			(width, height)= self.player_status.get_video_resolution()
			logging.debug("size : {0}x{1}".format(width, height))
			drawing_area = self.app.getitem("VideoZone")
			drawing_area.set_size_request(width, height)
			# gdkwindow = drawing_area.window
			logging.debug("trying to go fullscreen ...")
			# new_window = Gtk.Window(Gtk.WINDOW_TOPLEVEL)
			#new_window.fullscreen()
			#drawing_area.set_parent_window(new_window.get_parent_window())
			# self.player_status = Player_status(self.MPlayer)
			# self.player_status.play(filename)
			status = self.player_status
			status.set_playing()
			status.set_subtitles(subfile)
			#pylint: disable = E1101
			status.connect("play_ended", self.end_of_play)
		
		self.update_serie_view()	


	def search_subtitles(self, btn):#pylint: disable=W0613
		"""TODO : Upgrade to twisted
		async method for findind subtitles
		
		Subtitles finders simply write results in current season directory
		"""
		logging.debug("searching ... in a thread")
		chemin_serie = self.serie_model.get_current_serie()\
				.get_path_to_current_season()
		arguments = [self.serie_model, self.subtitle_downloader]
		methode = thr_sub_dl
		subdl_worker = threading.Thread(\
				name = "thread_sub"+chemin_serie, args = arguments, target = methode)
		subdl_worker.start()
		logging.debug("searching done ! ...")

	def subtitle_seek(self, treeview, path, column):#pylint: disable=W0613
		""" Callback when users wants to go to a subtitles instant in the video
		Action : sends a seek command to MPLayer to the date of current selected
		subtitle in subtitle view
		"""
		(model, itera)= treeview.get_selection().get_selected()
		time = model.get_value(itera, 0).start
		self.player_status.handle_seek(time)

	def subtitle_sync(self, button):#pylint: disable=W0613
		""" Callback when user wants to decay subtitles to a current time

		Action : sets the decay_subtitle value to MPLayer corresponding roughly 
		to the difference beetween :
		current time in the video, and selected subtitle time
		"""
		# getting datas
		treeview = self.app.getitem("SubtitlesTreeView")
		(model, itera)= treeview.get_selection().get_selected()
		time = model.get_value(itera, 0).start.ordinal / 1000
		in_video_time = self.player_status.get_current_time()
		sub_delay = self.player_status.get_subtitles_delay()

		# calculating 
		delay = time - in_video_time
		logging.info("time = {0} ; \
				in video time = {1} ;\
				sub_delay calculated = {}"
				.format(time, in_video_time, sub_delay))

		# sending command
		self.player_status.set_subtitles_delay(delay)

	def playing(self):
		""" Action function : sets the interface in playing mode """
		for nom in self.play_buttons:
			self.app.getitem(nom).set_sensitive(False)
		return ( self.current_process == None )
	

	def update_serie_view(self):
		""" Callback when [lots of calls ]
		Action : 
		* Reads the current Store configuration to Serie Manager (current serie, ...)
		* and sets up interface accordingly
		"""

		# just to update season view at the moment, 
		# no way to change serie other than manually
		# TODO: watch if that changes

		self.update_season_view()

	def update_season_view(self):
		""" Callback when season number in serie changed.
		Action : 
		* update the serie & episode view
		"""

		serie = (self.serie_model.current_serie)
		newsaison = int(serie.season_num)

		spin = self.app.getitem("numSaisonSpin")
		spin.set_value(newsaison)

		self.update_episode_view()

	@property
	def serie(self):
		""" getter for current selected serie""" 
		return self.serie_model.current_serie

	
	def update_episode_view(self):
		""" Callback when a new episode must be shown
		Action :
		* update episode number
		* loads sutitles & video name candidates
		"""
		serie = self.serie_model.current_serie
		newep =  serie.season.episode.number
		
		self.app.getitem("numEpSpin").set_value(newep)
		self.app.getitem("skipTimeSpin").set_value(serie.get_skip_time())
		self.app.getitem("decayTimeSpin").set_value(serie.get_decay_time())

		vid_list = serie.get_video_list()
		logging.info("Videos !!! nb:{}".format(len(vid_list)))
		logging.info(vid_list)

		if len (vid_list) > 0 :
			self.app.getitem("NomficLabel").set_text(vid_list[0])
		else:
			episode = Episode(serie, serie.season, newep)
			self.add_video_finder(episode)
			self.app.getitem("NomficLabel").set_text("")
		
		self.update_subs()




	def add_video_finder(self, episode):
		""" Ubuesque code cascade & design trigerring
		"""
		controller = self.video_finder_controller
		controller.add_video_finder(self.app, episode)

	def selected_serie_changed(self, widg):
		"""Callback when selected UI série changes
		Actions:
		* updates the serie Model 
		* then triggers UI update 
		"""
		itera = widg.get_active_iter()
		if itera != None:
			val = widg.get_model().get_value(widg.get_active_iter(), 0)
			self.serie_model.current_serie = val
			self.update_serie_view()
	
	def put_monitor_on_saison(self):
		""" Set up monitoring of directory
		* Installs monitors on current season directory
		* Installs Callbacks on Season

		Todo : Refactor to get a "Directory" Model class
		"""
		path = self.serie_model.get_current_serie().get_path_to_current_season()
		self.monitor_serie = None
		path = Gio.File.new_for_path(path)
		if(path):
			self.monitor_serie = path.monitor_directory(Gio.FileMonitorFlags.NONE, None)
			self.monitor_serie.connect("changed", self.update_subs_and_file)

	def update_season_number(self, widg):
		""" Callback when selected Season changes
		Actions :
			* update Model
			* Triggers UI update
			"""
		logging.info("saison courante num changed ?")
		self.serie_model.current_serie.season = int(widg.get_value())
		
		self.update_season_view()
		self.put_monitor_on_saison()

	def update_episode_number(self, widg):
		""" Callback When current episode changes
		Actions :
		* updates Model
		* update UI accordingly
		"""
		logging.info("ep courant num changed ?")
		self.serie_model.current_serie.season.episode = int(widg.get_value())
		
		logging.debug(self.serie_model.current_serie.season.episode.number)

		self.update_episode_view()

	def update_skip_time(self, widg):
		""" Callbacks when user updates the skip time
		Action : 
		* updates Model 
		"""
		logging.info("skip time changed ?")
		self.serie_model.serie.set_skip_time(int(widg.get_value()))

	def update_decay_time(self, widg):
		""" Callback when decay time changes
		Actions: 
		* updates Model
		"""
		logging.info("decay time changed ? {}".format(widg.get_value()))

		self.serie_model.get_current_serie().set_decay_time(int(widg.get_value()))

	def update_fps(self, widg):
		""" Callback when User changes the FPS value on the view
		Action : updates Model
		TODO: delete or debug
		"""
		logging.info("fps time changed ?")
		val = None 
		logging.info("changed" + val )
		self.serie_model.get_current_serie().set_fps(val)

	def update_subtitle_file(self, widg):
		""" Callback when user changes selected subtitle file
		Action : updates Model
		"""
		itera = widg.get_active_iter()
		# logging.info(type(itera), itera)
		if itera != None:
			val = widg.get_model().get_value(widg.get_active_iter(), 0)
			self.serie_model.get_current_serie().set_subtitle_file(val)

			absolute_subfile = os.path.join(
					self.serie_model\
							.get_current_serie()\
							.get_path_to_current_season(),
					val)

			subtitle_file_model = ui.subtitles.SubtitlesStore(absolute_subfile)
			self.app.getitem("SubtitlesTreeView")\
					.set_model(subtitle_file_model.get_model())

	def update_subs(self):
		""" Callback The available subtitles are modified 
		Action : updates Model, updtates ui
		"""
		liste = self.serie_model.current_serie.season.episode.get_subtitle_list()
		
		logging.info("Subs !! nb:{}".format(len(liste)))
		if len(liste) == 0:
			self.search_subtitles(None)
		
		box = self.app.getitem("CandidateSubsCombo")

		ui.ui_utils.populate_combo_with_items(box, liste)
		

		self.update_subtitle_file(box)
		
	def end(self, widg):
		""" Callback to clean application & exit """

		self.player_status.end_player()
		# Gtk.main_quit(widg)
		reactor.stop() #pylint: disable = E1101

	def video_keypress(self, widgi, event):#pylint: disable=W0613
		""" Callback intended to send key events to MPlayer 
		when in a subwindow on the UI
		TODO : Currently unused, needs a branch.
		"""
		logging.info(event.hardware_keycode)
		#self.player
		logging.info("keypressed")
		# logging.info(keyval)

	def set_manager(self, man):
		""" Setter for the main Available Séries manager """
		self.manager = man

