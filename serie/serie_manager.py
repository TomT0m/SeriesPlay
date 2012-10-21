#! /usr/bin/python
#encoding:utf-8
""" managing data about series """

# from utils.cli import CommandExecuter, CommandLineGenerator, \
# 		ConfigManager, FileNameError

# from trace import trace


from logging import debug, info

class SeriesManager(object):
	""" Base class model for 
	stored informations retrieval
	"""

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


class Episode:
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
		return self._season
	@property
	def number(self):
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


class Serie:
	""" Base class for defining a serie """
	def __init__(self, name):
		self.name = name
		self._season_num = self.get_stored_current_season_number()
		self.num_episode = self.get_next_episode_num()
		self.skiptime = 0
		self.decaytime = 0
		self.fps = ""
		self.subtitle_file_name = None

	@property
	def season_num(self):
		return self._season_num

	@property
	def episode_num(self):
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

	def set_current_season_number(self, num):
		""" Current season setter """
		self.season_num = num

	def get_season(self, number):
		pass

	@property
	def season(self):
		return self.get_season(self.get_current_season_number())

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
	def __init__(self, serie, number):
		self._serie = serie
		self._number = number

	@property
	def number(self):
		return self._number

	@property
	def serie(self):
		return self._serie

	@property
	def episode(self):
		""" implementation dependant : 
		getter for current episode object
		"""
		pass

	@property
	def episode_number(self):
		return self._episode_number

class SeriesData(object):
	""" Base class for series set"""
	def __init__(self, current_serie, series):
		self.series = {}
		self.current_serie_name = current_serie
	
		for serie in series :
			info("Creating serie {}".format(serie))
			self.series[serie] = None
		self.add_serie(current_serie)	

	@property
	def current_serie(self):
		return self.series[self.current_serie_name]

	@current_serie.setter
	def set_current_serie_by_name(self, serie):
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
		debug("pappy adding serie {}".format(name))
	
