#! /usr/bin/python
#encoding:utf-8
""" managing data about series, bash store implementation """
import os
import numbers
from logging import debug, info

from serie_manager import SeriesManager, Serie, Episode, SeriesData

from utils.cli import CommandExecuter, CommandLineGenerator, \
		ConfigManager, FileNameError

class BashSeriesManager(SeriesManager):
	""" Base class model for a set of Series managed by a bash store """

	config_file_season_name = ".play_conf"	
	config_file_serie_name = ".play_season"
	config_file_abs_name = "~/.play_season"

	path_to_series_var = "BASE"
	play_current_episode_var = "CUR"
	skip_time_var = "GENERICTIME"
	decay_time_var = "DECALAGESUB"
	serie_name_var = "NAME"
	fps_var = "SUBFPS"

	def __init__(self, config_file = config_file_abs_name):
		SeriesManager.__init__(self)
		self.executer = CommandExecuter()
		self.config_file_abs_name = config_file 
		self.config_manager = ConfigManager( config_file )
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

	def get_current_stored_episode(self, serie_name, season_num):
		""" Returns current episode number in disk store
		"""
		ficname = ""

		season_path = self.get_path_to_season(serie_name, 
				season_num) 
		ficname = os.path.join( season_path, \
				self.config_file_season_name )

		if os.path.exists(ficname):
			return self.read_num_conf_var(ficname, \
					self.play_current_episode_var)
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


class BashManagedEpisode(Episode):
	""" Episode info managed by bash scripts

	TODO : finish implementation separation
	"""
	def __init__(self, serie, season_num, num_ep):
		Episode.__init__(self, serie, season_num, num_ep)	
	
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
		num = self.manager.\
			get_current_stored_episode(self.name, \
					self.get_current_season_number())
		return num

	def get_next_episode(self):
		""" next unseen episode number in season"""
		return BashManagedEpisode(self, 
				self.get_current_season_number(), 
				self.get_next_episode_num())


	def get_next_episode_in_season(self, season_num):
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
		self.set_current_episode_number(self.get_next_episode_in_season(num))

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


