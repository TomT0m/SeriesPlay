#! /usr/bin/python
#encoding:utf-8
""" managing data about series, bash store implementation """
import os
import numbers
import glob, re

from logging import debug, info

from serie_manager import SeriesManager, Serie, Episode, \
		Season, SeriesData

from utils.cli import CommandExecuter, \
		ConfigManager, FileNameError

from app.config import Config

class BashSeriesStore(SeriesManager):
	""" Base class model for a set of Series managed by a bash store """

	config_file_season_name = ".play_conf"	
	config_file_serie_name = ".play_season"
	def_config_file_abs_name = os.path.expanduser("~/.play_season")

	path_to_series_var = "BASE"
	play_current_episode_var = "CUR"
	skip_time_var = "GENERICTIME"
	decay_time_var = "DECALAGESUB"
	serie_name_var = "NAME"
	fps_var = "SUBFPS"

	def __init__(self, config_file = def_config_file_abs_name):
		SeriesManager.__init__(self)
		self.executer = CommandExecuter()
		self.config_file_abs_name = config_file 
		self.config_manager = ConfigManager( config_file )
		self.config = Config(config_file) 

# paths generator
	def get_global_config_file(self):
		""" Get Path to global user config file """
		return os.path.expanduser(self.config_file_abs_name)

	def get_absolute_path(self):
		""" Get Root Path for Series storing"""
		base = self.config_manager.read_conf_var(self.get_global_config_file(), \
						self.path_to_series_var)
		base = os.path.expanduser(base)
		info("reading conf from file : {0}".format(base))
		debug("base path : {}".format(base))
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
		name = self.get_current_serie_name()
		return self.get_path_to_current_season_of(name) 

	def get_serie_configfile(self, name):
		""" Returns configfile for serie name @name """
		return os.path.join(self.get_path_to_serie(name), self.config_file_serie_name)

	def get_season_configfile(self, name, season):
		""" returns season configfile for serie 'name' season 'season' """
		return os.path.join(self.get_path_to_season(name, season), 
				self.config_file_season_name)

	def get_path_to_current_season_of(self, name):
		""" Get path to current season of a particular serie @name
		"""
		num = self.get_stored_current_season_number(name)
		return self.get_path_to_season(name, num)

	def get_path_to_season(self, name, numsaison):
		""" Get path to season @numseason of serie @name
		"""
		serie_path = self.get_path_to_serie(name)
		pattern = '[Ss]*{}'.format(numsaison)

		full_pattern = os.path.join(serie_path, pattern)
		candidates = glob.glob(full_pattern)
		if len(candidates) == 0:
			raise Exception("Season {} path not found for '{}'".format(numsaison, name))

		return candidates[0]

	
# config management 
	def read_conf_var(self, config_file_path, var_name, default=None):
		""" Gets a value in a 'key=value' file format 
		@config_file_path : the file
		@var_name : the key
		"""
		try:
			return self.config_manager.read_conf_var(config_file_path, var_name)
		finally:
			pass
		return default
	
	def write_conf_var(self, config_file_path, var_name, value):
		""" Writes a value in a 'key=value' file format 
		@config_file_path : the file
		@var_name : the key
		@value : the value
		"""
		return self.config_manager.write_conf_var(config_file_path, var_name, value)
		
	def read_num_conf_var(self, config_file_path, var_name, default = None):
		""" Reads a numeric value in a 'key=value' file format 
		@config_file_path : the file
		@var_name : the key
		"""
		value = default
		try:
			value = self.config_manager.read_num_conf_var(config_file_path, var_name)
		except Exception:
			pass
		return value 

		# finally:
		#	return default

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
	def get_current_serie_name(self):
		""" Returns the name of current serie """
		return self.config_manager.read_var("NAME")

	def get_stored_current_season_number(self, name):
		""" Returns season number of current serie """

		serie_conf_file = self.get_serie_configfile(name)
		num = self.read_num_conf_var(serie_conf_file, "SEASON", 1)
	
		return num

	def get_serie_list(self):
		""" Returns the list of series name
		on the directory """
		serie_path = self.get_absolute_path()
		dirs = [ x for x in os.listdir(serie_path) 
				if os.path.isdir(os.path.join(serie_path, x)) ]
		return dirs

	def create_season_storage(self, serie_name, season_num):
		""" Create season directory for serie 'serie_name' season 'season_num'"""
		serie_path = self.get_path_to_serie(serie_name)
		dir_name = "Saison {}".format(season_num)
		
		full_season_path = os.path.join(serie_path, dir_name)
		os.mkdir(full_season_path)

		with open( self.get_season_configfile(serie_name, \
				season_num) ,'w') as fic:
			fic.write("""CUR='1'\nGENERICTIME='0'""")
		

	def get_current_stored_episode(self, serie_name, season_num):
		""" Returns current episode number in disk store
		"""
		ficname = ""
		season_path = None
		try:
			season_path = self.get_path_to_season(serie_name, \
				season_num)
		except Exception :
			self.create_season_storage(serie_name, season_num)
			season_path = self.get_path_to_season(serie_name, 
				season_num)

		ficname = os.path.join( season_path, \
				self.config_file_season_name )

		if os.path.exists(ficname):
			return self.read_num_conf_var(ficname, \
					self.play_current_episode_var)

		raise Exception("Unexisting config file {}".format(ficname))

	def get_subtitle_candidates(self, serie_name, season_num, num_ep):
		""" Returns the list of filename candidates for subtitles
		for @serie_name, for season number @season_num, episode @num_ep
		"""
		extensions = self.config.get_sub_extensions()
		
		result = self._get_candidates(serie_name, season_num, num_ep, extensions)
		return result
	
	def get_video_candidates(self, serie_name, season_num, num_ep):
		""" Returns the list of filename candidates for video
		for @serie_name, for season number @season_num, episode @num_ep
		""" 
		extensions = self.config.get_video_extensions()
		result = self._get_candidates(serie_name, season_num, num_ep, extensions)

		assert(len(result)>=0)
		return result

	def get_glob_pattern(self, season_num, num_ep, ext_list = None):
		""" Get globbing pattern
		"""
		patterns =  ['({season:02d}|{season:d}).*{ep:02d}',
				'[sS]{season:02d}[^0-9]( )?[xeE]{ep:02d}'
			]
		

		pattern = "({})".format("|".join(patterns))

		pattern = pattern.format(season = season_num, \
				ep = num_ep)


		if ext_list:
			pattern = '({}.*)\.({})'.format(pattern, "|".join(ext_list))

		return pattern

	def _get_candidates_in_path(self, path, season_num, num_ep, option):
		""" return matching filenames in path 'path' as "path/filename" list """
		result = []
		if(os.path.exists(path)):
			re_pattern = self.get_glob_pattern(season_num, num_ep, option)
			regex = re.compile(re_pattern)
			all_files = os.listdir(path)

			direct = [ x for x in all_files 
					if regex.search(x) ]
			result = direct

		return result

	def _get_candidates(self, serie_name, season_num, num_ep, option):
		"""  calls candidates finder bash script """
		path = self.get_path_to_season(serie_name, season_num)
		result = []
		if os.path.exists(path):

			all_files = os.listdir(path)

			direct = self._get_candidates_in_path(
					path, 
					season_num, num_ep, option) #[ x for x in all_files 
					#if regex.search(x) ]

			re_dir_pattern = re.compile(self.get_glob_pattern(season_num, num_ep))
			sub_dirs = [ os.path.join(path, x) for x in all_files 
					if os.path.isdir(os.path.join(path, x)) 
						and re_dir_pattern.search(x) ]
			subdir_candidates = [ candidate for dirs in sub_dirs 
					for candidate in \
							self._get_candidates_in_path(dirs, season_num, num_ep, option)
				]
			
			result = direct + subdir_candidates

		assert(len(result)>=0)
		return result

class BashManagedEpisode(Episode):
	""" Episode info managed by bash scripts

	TODO : finish implementation separation
	"""
	def __init__(self, serie, season, ep_number):
		Episode.__init__(self, serie, season, ep_number)
		# TODO: look for moving to dependancy injection framework
		assert(isinstance(season.number, numbers.Number))
		self.manager = serie.manager
	
class BashManagedSeason(Season):
	""" Season managed by config files"""
	def __init__(self, serie, number, ep_number = 0):
		self.manager = serie.manager
		self._serie = serie
		Season.__init__(self, serie, number, ep_number)
		# self._number = ep_number
		self._ep_number = self.serie.get_next_episode_in_season(self.number)

	@property
	def serie(self):
		""" Serie getter """ 
		return self._serie

	@property
	def episode(self):
		""" getter for current episode in this season""" 
		return BashManagedEpisode(self.serie, self, self._ep_number)
	
class BashManagedSerie(Serie):
	""" Serie managed by bash script for storage and info retrieval """

	def __init__(self, name, series_manager):
		self.manager = series_manager
		Serie.__init__(self, name)
		self.name = name
		skip = None
		fps = ""
		decay = None
		self.subtitle_file_name = None
		config = self.get_current_season_configfile()
		self.season_num = self.get_stored_current_season_number()
		
		if os.path.exists(config):
			try:
				skip = self.manager.read_num_conf_var(config, \
						self.manager.skip_time_var,
						0)
			finally:
				skip = 0
			try:
				fps = self.manager.read_conf_var(config, \
					self.manager.fps_var,
					"")
			except ConfigManager.KeyException:
				fps = ""
	
			decay = self.manager.read_num_conf_var(config, \
					self.manager.decay_time_var)
			liste_sub = self.get_subtitle_list()

			if len(liste_sub)>0:
				self.subtitle_file_name = liste_sub[0]
			self.season_num = self.manager\
					.get_stored_current_season_number(self.name)
		if skip != None :
			self.skiptime = skip 
		if decay != None :
			self.decaytime = decay
		
		self.fps = fps
	@property
	def season(self):
		""" Getter for current season object"""
		return self.get_season(self.season_num)
	#@property
	#def serie(self):
	def get_stored_current_season_number(self):
		""" return the stored current season number for this season"""
		
		assert(self.name != "" and self.name)
		
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
		# assert( i)
		return BashManagedEpisode(self, 
				self.get_current_season_number(), 
				self.get_next_episode_num())


	def get_next_episode_in_season(self, season_num):
		""" last seen episode number in season"""
		num = self.manager.get_current_stored_episode(self.name, season_num)
		if num != None:
			return num
		else:
			return 1

	def get_season(self, number):
		""" Getter for season object 'number' for this serie"""
		ep_number = self.get_next_episode_in_season(number)
		return BashManagedSeason(self, number, ep_number)

	def on_seen_episode(self):
		""" Callback when ep seen in this serie """
		self.season_num = self.get_current_season_number()
		self.season.num_episode = self.get_next_episode_num()
		self.manager.write_conf_var(
				self.manager.get_global_config_file(), 
				self.manager.serie_name_var, 
				self.name)

        
	def set_current_season_number(self, num):
		""" Setter for current season """
		if not isinstance(num, numbers.Number):
			raise ValueError(num)

		Serie.set_current_season_number(self, num)
		self.set_current_episode_number(self.get_next_episode_in_season(num))

	def set_current_episode_number(self, num):
		""" Setter for current episode number in current serie 
		and current season (TODO: check for deletion)"""
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
				self.season.number, self.season.episode.number)

	def get_video_list(self):
		""" Get candidates video list for current episode """
		result = self.manager.get_video_candidates(self.name, \
				self.season.number, self.season.episode.number)
		return result

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
		SeriesData.__init__(self, manager.get_current_serie_name(), liste)

	def get_base_path(self):
		""" Returns path of series storage """
		return self.manager.get_absolute_path()
	
	def add_serie(self, name):
		""" add a serie to the store, from his name """
		debug("fifis adding serie")
		self.series[name] = self.serie_factory.create_serie(name)

