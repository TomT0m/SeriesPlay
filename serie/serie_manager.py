#! /usr/bin/python
#encoding:utf-8
""" managing data about series """

from utils.cli import CommandExecuter, CommandLineGenerator, \
		ConfigManager, FileNameError

# from trace import trace

import numbers
import os

from logging import debug, info

class SeriesManager:
	""" Base class model for a set of Series """

	config_file_season_name = ".play_conf"	
	config_file_serie_name = ".play_season"
	config_file_abs_name = "~/.play_season"

	path_to_series_var = "BASE"
	play_current_episode_var = "CUR"
	skip_time_var = "GENERICTIME"
	decay_time_var = "DECALAGESUB"
	serie_name_var = "NAME"
	fps_var = "SUBFPS"
	def __init__(self):
		self.executer = CommandExecuter()

# paths generator
	def get_global_config_file(self):
		""" Get Path to global user config file """
		return os.path.expanduser(self.config_file_abs_name)

	def get_absolute_path(self):
		""" Get Root Path for Series storing"""
		base = self.read_conf_var(self.get_global_config_file(), \
						self.path_to_series_var)\
						.strip("\n")\
						.strip(" ")
		base = os.path.expanduser(base)
		info("reading conf from file : {0}".format(base))
		debug(base)
		if not os.path.exists(base):
			raise FileNameError(base)
		return base

	def get_path_to_serie(self, name):
		""" Get path to serie @name
		"""
		base = self.get_absolute_path()
		return os.path.join(base, name)

	def get_path_to_current_season(self):
		""" Get path to current season of currently viewed serie
		"""
		return self.executer.get_output(["series", "-g"])

	def get_path_to_current_season_of(self, name):
		""" Get path to current season of a particular serie @name
		"""
		return self.executer.get_output(["series", "-g", "-n", name])
	
	def get_path_to_season(self, name, numsaison):
		""" Get path to season @numseason of serie @name
		"""
		command = CommandLineGenerator("series")
		if not isinstance(numsaison, numbers.Number) :
			raise TypeError(numsaison)
		command.add_option_single("-g")
		command.add_option_param("-D", name)
		command.add_option_param("-n", str(numsaison))

		return self.executer.get_output(command.get_command())\
				.strip().rstrip("/") + "/"

	
# config management 
	def read_conf_var(self, config_file_path, var_name):
		""" Gets a value in a 'key=value' file format 
		@config_file_path : the file
		@var_name : the key
		"""
		return ConfigManager.read_conf_var(config_file_path, var_name)
	
	def write_conf_var(self, config_file_path, var_name, value):
		""" Writes a value in a 'key=value' file format 
		@config_file_path : the file
		@var_name : the key
		@value : the value
		"""
		return ConfigManager.write_conf_var(config_file_path, var_name, value)
		
	def read_num_conf_var(self, config_file_path, var_name):
		""" Reads a numeric value in a 'key=value' file format 
		@config_file_path : the file
		@var_name : the key
		"""
		return ConfigManager.read_num_conf_var(config_file_path, var_name)

	def get_conf_variable(self, name, numseason, var_name):
		""" Gets value of a variable stored for a specified @numseason season
		of a specified serie @name. """
		return self.read_conf_var(self.get_path_to_season(name, numseason), var_name)

	def get_num_conf_variable(self, name, numseason, var_name):
		""" same as get_conf_variable for a Numeric value """
		return self.read_num_conf_var(
				self.get_path_to_season(name, numseason), 
				var_name)


# useful data getters
	def get_current_serie(self):
		""" Returns the name of current serie """
		return self.executer.get_output(["series", "-C"]).strip().strip(" ")

	def get_stored_current_season_number(self, nom):
		""" Returns season number of current serie """
		res = self.executer.get_output(["series", "-N", "-D", nom]).strip()
		if res != "":
			return int(res)
		else:
			return None

	def get_serie_list(self):
		""" Returns the list of series name
		on the directory """
		debug("getting serie list")
		liste_en_chaine = CommandExecuter().get_list_output(["series","-l"])

		debug("got serie list")
		return liste_en_chaine

	def get_current_episode(self, serie_name, season_num):
		""" Returns the number of current episode in disk store
		"""
		ficname = ""
		try:
			ficname = self.get_path_to_season(serie_name, season_num) \
					+ self.config_file_season_name
		except ValueError| TypeError:
			return None

		if os.path.exists(ficname):
			try:
				num = int(self.read_conf_var(ficname, 
					self.play_current_episode_var)\
							.strip())
				return num
			except  ValueError | TypeError :
				return None
		return None

	def get_subtitle_candidates(self, serie_name, season_num, num_ep):
		""" Returns the list of filename candidates for subtitles
		for @serie_name, for season number @season_num, episode @num_ep
		""" 
		return self._get_candidates(serie_name, season_num, num_ep, "-L")
	
	def get_video_candidates(self, serie_name, season_num, num_ep):
		""" Returns the list of filename candidates for video
		for @serie_name, for season number @season_num, episode @num_ep
		""" 
		return self._get_candidates(serie_name, season_num, num_ep, "-V")

	def _get_candidates(self, serie_name, season_num, num_ep, option):
		"""  calls candidates finder bash script """
		path = self.get_path_to_season(serie_name, season_num)
                
		if os.path.exists(path):
			command_g = CommandLineGenerator("play")
			command_g.add_option_param("-e", unicode(num_ep))
			command_g.add_option_single(unicode(option))
			return self.executer\
					.get_list_output(command_g.get_command(), 
							cwd = path)
		else:
			return []





class Episode:
	""" Base class for episode information storage 
	"""
	def __init__(self, serie, season_num, num_ep):
		self.season_num = season_num
		self.serie = serie
		self.num_ep = num_ep
		self.skiptime = None
		self.decaytime = None
		self.fps = None
		self.subtitle_file_name = None

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

class BashManagedEpisode(Episode):
	""" Episode info managed by bash scripts

	TODO : finish implementation separation
	"""
	def __init__(self, serie, season_num, num_ep):
		Episode.__init__(self, serie, season_num, num_ep)	
	

class Serie:
	""" Base class for defining a serie """
	def __init__(self, name):
		self.name = name
		self.season_num = self.get_stored_current_season_number()
		self.num_episode = self.get_next_episode_num()
		self.skiptime = 0
		self.decaytime = 0
		self.fps = ""
		self.subtitle_file_name = None

	def get_next_episode_num(self):
		""" next unseen episode number in season"""
		pass

	def get_current_season_number(self):
		""" Current season getter"""
		return self.season_num

	def get_stored_current_season_number():
		""" return last know seen season number,
		ie. the stored one
		"""
		pass

	def get_current_episode_number(self):
		""" Current episode getter"""
		return self.num_episode

	def set_current_season_number(self, num):
		""" Current season setter"""
		self.season_num = num

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


class BashManagedSerie(Serie):
	""" Serie managed by bash script for storage and info retrieval """

	def __init__(self, name, series_manager):
		self.manager = series_manager
		Serie.__init__(self, name)
		skip = None
		fps = ""
		decay = None
		self.subtitle_file_name = None
		config = self.get_current_season_configfile()
		self.season_num = 1
		if os.path.exists(config):	
			skip = self.manager.read_num_conf_var(config, \
					self.manager.skip_time_var)
			fps = self.manager.read_conf_var(config, \
					self.manager.fps_var)
			if fps == None:
				fps = ""
	
			decay = self.manager.read_num_conf_var(config, \
					self.manager.decay_time_var)
			liste_sub = self.get_subtitle_list()

			if len(liste_sub)>0:
				self.subtitle_file_name = liste_sub[0]
			#self.season_num = self.manager\
			#		.get_stored_current_season_number(self.name)
		if skip != None :
			self.skiptime = skip 
		if decay != None :
			self.decaytime = decay 
		self.fps = fps.strip()
	
	def get_stored_current_season_number(self):
		""" return the stored current season number for this season"""
		return self.manager.get_stored_current_season_number(self.name)
	
	def get_current_season_number(self):
		""" return the stored season number for this season"""
		return self.season_num

	def get_next_episode_num(self):
		""" returns number of next episode to be seen in current season """
		try:
			num = self.manager.\
					get_current_episode(self.name, \
					self.get_current_season_number())
		except ValueError | TypeError:
			num = None

		if num != None:
			return num
		else:
			return 1

	def get_next_episode(self):
		""" next unseen episode number in season"""
		return BashManagedEpisode(self, 
				self.get_current_season_number(), 
				self.get_next_episode_num())


	def get_lastseen_ep_in_season(self, season_num):
		""" last seen episode number in season"""
		num = self.manager.get_current_episode(self.name, season_num)
		if num != None:
			return num
		else:
			return 1

	def on_seen_episode(self):
		self.season_num = self.get_current_season_number()
		self.num_episode = self.get_next_episode_num()
		self.manager.write_conf_var(
				self.manager.get_global_config_file(), 
				self.manager.serie_name_var, 
				self.name)

        
	def set_current_season_number(self, num):
		if not isinstance(num, numbers.Number):
			raise ValueError(num)

		Serie.set_current_season_number(self, num)
		self.set_current_episode_number(self.get_lastseen_ep_in_season(num))

	def set_current_episode_number(self, num):	
		Serie.set_current_episode_number(self, num)
		debug("setting num ep courant")
		nomfic = self.get_current_season_configfile()
		skip = decay = 0
		fps = ""
		if os.path.exists(nomfic):
			skip = self.manager\
					.read_num_conf_var(nomfic, self.manager.skip_time_var)
			fps = self.manager\
					.read_conf_var(nomfic, self.manager.fps_var)
			decay = self.manager\
					.read_num_conf_var(nomfic, self.manager.decay_time_var)
			
			if skip != None :
				self.skiptime = skip

			if decay != None :
				self.decaytime = decay

			if fps != None :
				self.fps = fps
		else:
			pass

	def get_name_of_config_file(self, season):
		""" Get storage filename for @season of current serie """
		if not isinstance(season, numbers.Number):
			raise TypeError(season)
		return os.path.join(self.manager.get_path_to_season(self.name, season), \
				self.manager.config_file_season_name)

	def get_name_of_serie_config_file(self):
		""" Get storage filename for current season of current serie """
		return os.path.join(self.manager.get_path_to_serie(self.name), \
				self.manager.config_file_serie_name)

	def get_path_to_serie(self):
		""" Get path storage of current serie """
		return self.manager.get_path_to_serie(self.name)

	def get_current_season_configfile(self):
		""" Get storage of current serie filename """
		return os.path.join(
				self.manager.get_path_to_season(self.name, 
					self.season_num), 
				self.manager.config_file_season_name)

	def get_path_to_current_season(self):
		""" Get path to current season of current serie filename """
		return self.manager.get_path_to_season(self.name, 
				self.season_num)

	def get_path_to_season(self, season):
		""" Get path to current season of current serie filename """
		return self.manager.get_path_to_season(self.name, season)

	def get_subtitle_list(self):
		""" Get candidates subs list for current episode """
		return self.manager.get_subtitle_candidates(self.name, \
				self.season_num, self.num_episode)

	def get_video_list(self):
		""" Get candidates video list for current episode """
		return self.manager.get_video_candidates(self.name, \
				self.season_num, self.num_episode)

	def get_absolute_filename(self, filename):
		""" gets the absolute filename of a relative file of serie"""
		return os.path.join(self.manager\
				.get_path_to_season(self.name, self.season_num), \
				filename)

	def save_current_episode_parameters(self):
		""" TODO : to implement ?"""
		pass	

class BashManagedSerieFactory:
	""" Factory for serie managed by bash scripts """
	def __init__(self, manager):
		self.manager = manager

	def create_serie(self, name):
		""" Factory method, serie """
		return BashManagedSerie(name, self.manager)
	
	def create_serie_manager(self):
		""" Factory method, serie list """
		return BashManagedSeriesData(self.manager, self)


class SeriesData(object):
	""" Base class for series set"""
	def __init__(self, current_serie, series):
		self.series = {}
		self.current_serie_name = current_serie
	
		for serie in series :
			info("Creating serie {}".format(serie))
			self.series[serie] = None
		# self.series[currentSerie]= Serie(currentSerie)

		self.current_serie = self.series[current_serie]

	def set_current_serie_by_name(self, serie):
		""" Sets current serie object """
		self.current_serie_name = serie

		if self.series[serie] == None:
			self.add_serie(serie)
		
		self.current_serie = self.series[serie]
	
	def get_current_serie(self):
		""" gets current serie object """
		self.set_current_serie_by_name(self.current_serie_name)
		return self.current_serie

	def add_serie(self, name):
		"""Stupid test function to delete """
		debug("pappy adding serie {}".format(name))
	
class BashManagedSeriesData(SeriesData):
	""" Serie info retrieved by bash scripts, historical"""
	def __init__(self, manager, serie_factory = None):
		# SeriesData.__init__(self)
		self.manager = manager
		self.serie_factory = serie_factory
		if not self.serie_factory:
			self.serie_factory = BashManagedSerieFactory(manager)
		
		liste = manager.get_serie_list()
		super(BashManagedSeriesData, self)\
				.__init__(manager.get_current_serie(), liste)

	def get_base_path(self):
		""" Returns path of series storage """
		return self.manager.get_absolute_path()
	
	def add_serie(self, name):
		""" add a serie to the store, from his name """
		info("fifis adding serie")
		self.series[name] = self.serie_factory.create_serie(name)


