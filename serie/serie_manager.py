#! /usr/bin/python
#encoding:utf-8
""" managing data about series """



from logging import debug, info
from snakeguice import inject
from snakeguice.injector import IInjector

from gi.repository import GObject 

class SeriesStore(object):
	""" Base class model for 
	stored informations retrieval
	"""
	def __init__(self):
		raise NotImplementedError("SeriesStore is abstract") 
	def get_stored_current_season_number(self, nom):
		""" Returns season number of current serie """
		pass

	def get_serie_list(self):
		""" Returns the list of series name """
		pass

	def get_current_stored_episode(self, serie_name, season_num):
		""" Returns current episode number in disk store
		"""
		pass

	def get_subtitle_candidates(self, serie_name, season_num, num_ep):
		""" Returns the list of filename candidates for subtitles
		for @serie_name, for season number @season_num, episode @num_ep
		"""
		pass

	def get_video_candidates(self, serie_name, season_num, num_ep):
		""" Returns the list of filename candidates for video
		for @serie_name, for season number @season_num, episode @num_ep
		"""
		pass


class Episode(object):
	""" Base class for episode information storage 
	"""
	def __init__(self, serie, season, num_ep):
		self._season = season
		self.serie = serie
		self.num_ep = num_ep
		self.skiptime = None
		self.decaytime = None
		self.fps = None
		self.subtitle_file_name = None
	@property
	def season(self):
		""" getter for episode's Season object """
		return self._season

	@property
	def number(self):
		""" Getter for episode number in season """
		return self.num_ep

	def get_skip_time(self):
		""" getter for skiptime (time to skeep at the episode beginning) """
		return self.skiptime	

	def set_skip_time(self, skiptime):
		""" setter """ 
		self.skiptime = skiptime
		
	def get_decay_time(self):
		""" getter for subtitle decay """
		return self.decaytime	

	def set_decay_time(self, decaytime):
		""" setter for subtitle decay """
		self.decaytime = decaytime

	def get_fps(self):
		""" fps getter """ 
		return self.fps

	def set_fps(self, fps):
		""" fps setter """ 
		self.fps = fps

	def get_subtitle_list(self):
		""" get subtitles file candidates list for episode """
		pass
	
	def get_video_list(self):
		""" get video file candidates list for episode """
		pass

	def set_subtitle_file(self, subfile):
		""" set chosen subtitle file """
		self.subtitle_file_name = subfile

	def get_subtitle_file(self):
		""" get chosen subtitle file """
		return self.subtitle_file_name

	def get_video_filename(self):
		""" get chosen video file 
		TODO: ?"""
		pass


class Serie(object):
	""" Base class for defining a serie """
	def __init__(self, name):
		self._name = name
		self._season_num = self.get_stored_current_season_number()
		self.num_episode = self.get_next_episode_num()
		self.skiptime = 0
		self.decaytime = 0
		self.fps = ""
		self.subtitle_file_name = None
	
	@property
	def name(self):
		""" name getter """
		return self._name

	@property
	def season_num(self):
		""" Getter for current season number """
		return self._season_num

	@season_num.setter
	def season_num(self, num):
		""" setter for current season number"""
		self._season_num = num
	
	@property
	def episode_num(self):
		""" Getter for next episode in current season """
		return self.get_next_episode_num()

	def get_next_episode_num(self):
		""" next unseen episode number in season"""
		pass
	
	def get_stored_current_season_number(self):
		""" return last know seen season number,
		ie. the stored one
		"""
		pass

	def get_current_episode_number(self):
		""" Current episode getter """
		return self.num_episode

	
	def get_season(self, number):
		""" Getter for season number "number" of serie"""
		pass

	@property
	def season(self):
		""" Getter for current season object"""
		return self.get_season(self.season_num)

	def set_current_episode_number(self, num):
		""" Current episode setter"""
		self.num_episode = num

	def on_seen_episode(self):
		""" To call when an episode has just been seen"""
		pass

	def get_skip_time(self):
		""" Time to skip at the beginning of an episode (generic ?)"""
		return self.skiptime	

	def set_skip_time(self, skiptime):
		""" setter Time to skip at the beginning of an episode (generic ?)"""
		self.skiptime = skiptime

	def get_decay_time(self):
		""" getter for deflault decay subtitles time """ 
		return self.decaytime	

	def set_decay_time(self, decaytime):
		""" setter for deflault decay subtitles time """ 
		self.decaytime = decaytime

	def get_fps(self):
		""" Video FPS getter """
		return self.fps

	def set_fps(self, fps):
		""" Video FPS setter """
		self.fps = fps

	def get_subtitle_list(self):
		""" get list of files candidates to be subtitles 
		of current episode """
		pass
	
	def get_video_list(self):
		""" get list of files candidates to be subtitles 
		of current episode """
		pass

	def set_subtitle_file(self, subfile):
		""" set chosen subtitle """
		self.subtitle_file_name = subfile

	def get_subtitle_file(self):
		""" get chosen subtitle """
		return self.subtitle_file_name

	def save_current_episode_parameters(self):
		""" TODO: To Implement : a per episode config"""
		pass 

	def set_next_episode(self):
		""" on episode seen : update serie state 
		to point to next available episode"""
		pass	

class Season(object):
	""" Season object"""
	def __init__(self, serie, number, ep_number):
		self._serie = serie
		self._number = number
		self._ep_number = ep_number

	@property
	def number(self):
		""" Season number getter """
		return self._number

	@property
	def serie(self):
		""" serie getter """
		return self._serie

	@property
	def episode(self):
		""" implementation dependant : 
		getter for current episode object
		"""
		pass
	@property
	def ep_number(self):
		""" Current episode number in season property getter """
		return self._ep_number

	@ep_number.setter
	def ep_number(self, number):
		""" Setter """
		self._ep_number = number


class SeriesData(object):
	""" Base class for series set"""
	@inject(injector = IInjector)
	def __init__(self, injector):
		self.series = {}
		self.injector = injector
		
		self.store = injector.get_instance(SeriesStore)
		

		self.current_serie_name = self.store.get_current_serie_name()
		lseries = self.store.get_serie_list()

		info("Creating series ...") # .format(nserie))
		for nserie in lseries :
			info("Creating serie {}".format(nserie))
			self.series[nserie] = self.add_serie(nserie)

	@property
	def current_serie(self):
		""" getter : selected serie """
		res = self.series[self.current_serie_name]
		if not res:
			self.add_serie(self.current_serie_name)

		return self.series[self.current_serie_name]

	@current_serie.setter
	def current_serie(self, serie):
		""" Sets current serie object """
		self.current_serie_name = serie

		if self.series[serie] == None:
			self.add_serie(serie)
		
		# self.current_serie = self.series[serie]
	
	def get_current_serie(self):
		""" gets current serie object """
		return self.current_serie

	def add_serie(self, name):
		"""Stupid test function to delete """
		raise NotImplementedError("wow")

	def get_serie_list(self):
		""" returns """
		return self.series
