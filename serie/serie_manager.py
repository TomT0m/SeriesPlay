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
		return os.path.expanduser(self.config_file_abs_name)

	def get_absolute_path(self):
		base = self.read_conf_var(self.get_global_config_file(), \
						self.path_to_series_var)\
						.strip("\n")\
						.strip(" ")
		base = os.path.expanduser(base)
		info("reading conf from file : {0}".format(base))
		base = os.path.expandvars(base)
		debug(base)
		if not os.path.exists(base):
			raise FileNameError(base)
		return base

	def get_path_to_serie(self, nom):
		base = self.get_absolute_path()
		return os.path.join(base, nom)

	def get_path_to_current_season(self):
		return self.executer.get_output(["series", "-g"])

	def get_path_to_current_season_of_serie(self, name):
		return self.executer.get_output(["series", "-g", "-n", name])
	
	def get_path_to_season(self, nom, numsaison):
		command = CommandLineGenerator("series")
		if not isinstance(numsaison, numbers.Number) :
			raise TypeError(numsaison)
		command.add_option_single("-g")
		command.add_option_param("-D", nom)
		command.add_option_param("-n", str(numsaison))

		return self.executer.get_output(command.get_command())\
				.strip().rstrip("/") + "/"

	
# config management 
	def read_conf_var(self, config_file_path, var_name):
		return ConfigManager.read_conf_var(config_file_path, var_name)
	
	def write_conf_var(self, config_file_path, var_name, value):
		return ConfigManager.write_conf_var(config_file_path, var_name, value)
		
	def read_num_conf_var(self, config_file_path, var_name):
		return ConfigManager.read_num_conf_var(config_file_path, var_name)

	def get_conf_variable(self, nom, numsaison, var_name):
		return self.read_conf_var(self.get_path_to_season(nom, numsaison), var_name)

	def get_num_conf_variable(self, nom, numsaison, var_name):
		return self.read_num_conf_var(
				self.get_path_to_season(nom, numsaison), 
				var_name)


# useful data getters
	def get_current_serie(self):
		return self.executer.get_output(["series", "-C"]).strip().strip(" ")

	def get_num_current_saison(self, nom):
		res = self.executer.get_output(["series", "-N", "-D", nom]).strip()
		if res != "":
			return int(res)
		else:
			return None

	# @trace
	def get_serie_list(self):
		print("getting serie list")
		liste_en_chaine = CommandExecuter().get_list_output(["series","-l"])

		print("got serie list")
		return liste_en_chaine

	def get_current_episode(self, nom_serie, num_saison):
		ficname = ""
		try:
			ficname = self.get_path_to_season(nom_serie, num_saison) \
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

	def get_subtitle_candidates(self, nom_serie, num_saison, num_ep):
		return self.get_candidates(nom_serie, num_saison, num_ep, "-L")
	
	def get_video_candidates(self, nom_serie, num_saison, num_ep):
		return self.get_candidates(nom_serie, num_saison, num_ep,"-V")

	def get_candidates(self, nom_serie, num_saison, num_ep, option):
		path = self.get_path_to_season(nom_serie, num_saison)
                
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
	def __init__(self, serie, num_saison, num_ep):
		self.num_saison = num_saison
		self.serie = serie
		self.num_ep = num_ep
		self.skiptime = None
		self.decaytime = None
		self.fps = None
		self.subtitle_file_name = None

	def get_subtitles(self):
		pass

	def get_skip_time(self):
		return self.skiptime	

	def set_skip_time(self, skiptime):
		self.skiptime = skiptime
		
	def get_decay_time(self):
		return self.decaytime	

	def set_decay_time(self, decaytime):
		self.decaytime = decaytime

	def get_fps(self):
		return self.fps

	def set_fps(self, fps):
		self.fps = fps

	def get_subtitle_list(self):
		pass
	
	def get_video_list(self):
		pass

	def set_subtitle_file(self, subfile):
		self.subtitle_file_name = subfile

	def get_subtitle_file(self):
		return self.subtitle_file_name

	def get_video_filename(self):
		pass

	def try_guess_name(self):
		pass	


class BashManagedEpisode(Episode):
	def __init__(self, serie, num_saison, num_ep):
		Episode.__init__(self, serie, num_saison, num_ep)	
	

class Serie:
	""" Base class for defining a serie """
	def __init__(self, nom):
		self.nom = nom
		self.num_saison = self.get_num_derniere_saison_vue()
		self.num_episode = self.get_num_prochain_episode()
		self.skiptime = 0
		self.decaytime = 0
		self.fps = ""
		self.subtitle_file_name = None

	def get_num_derniere_saison_vue(self):
		""" Last seen season getter"""
		pass

	def get_num_prochain_episode(self):
		""" next unseen episode number in season"""
		pass

	def get_num_saison_courante(self):
		""" Current season getter"""
		return self.num_saison

	def get_num_episode_courant(self):
		""" Current episode getter"""
		return self.num_episode

	def set_num_saison_courante(self, num):
		""" Current season setter"""
		self.num_saison = num

	def set_num_episode_courant(self, num):
		""" Current episode setter"""
		self.num_episode = num

	def episode_vu(self):
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
		pass
	
	def get_video_list(self):
		pass

	def set_subtitle_file(self, subfile):
		self.subtitle_file_name = subfile

	def get_subtitle_file(self):
		return self.subtitle_file_name

	def save_current_episode_parameters(self):
		pass 


class BashManagedSerie(Serie):
	def __init__(self, name, series_manager):
		self.manager = series_manager
		Serie.__init__(self, name)
		skip = None
		fps = ""
		decay = None
		self.subtitle_file_name = None
		if os.path.exists(self.get_name_of_current_season_config_file()):	
			skip = self.manager.read_num_conf_var( \

					self.get_name_of_current_season_config_file(), \
							self.manager.skip_time_var)
			fps = self.manager.read_conf_var(\
					self.get_name_of_current_season_config_file(), \
					self.manager.fps_var)
			if fps == None:
				fps = ""
	
			decay = self.manager.read_num_conf_var(\
					self.get_name_of_current_season_config_file(), \
					self.manager.decay_time_var)
			liste_sub = self.get_subtitle_list()

			if len(liste_sub)>0:
				self.subtitle_file_name = liste_sub[0]
		if skip != None :
			self.skiptime = skip 
		if decay != None :
			self.decaytime = decay 
		self.fps = fps.strip()
	
	def get_num_derniere_saison_vue(self):
		return self.manager.get_num_current_saison(self.nom)

	def get_num_prochain_episode(self):
		try:
			num = self.manager.\
					get_current_episode(self.nom, \
					self.get_num_saison_courante())
		except ValueError | TypeError:
			num = None

		if num != None:
			return num
		else:
			return 1

	def get_next_episode(self):
		return BashManagedEpisode(self, 
				self.get_num_derniere_saison_vue(), 
				self.get_num_prochain_episode())


	def get_num_dernier_episode_vu_in_season(self, num_saison):
		num = self.manager.get_current_episode(self.nom, num_saison)
		if num != None:
			return num
		else:
			return 1

	def episode_vu(self):
		self.num_saison = self.get_num_derniere_saison_vue()
		self.num_episode = self.get_num_prochain_episode()
		self.manager.write_conf_var(
				self.manager.get_global_config_file(), 
				self.manager.serie_name_var, 
				self.nom)

        
	def set_num_saison_courante(self, num):
		if not isinstance(num, numbers.Number):
			raise ValueError(num)

		Serie.set_num_saison_courante(self, num)
		self.set_num_episode_courant(self.get_num_dernier_episode_vu_in_season(num))

	def set_num_episode_courant(self, num):	
		Serie.set_num_episode_courant(self, num)
		debug("setting num ep courant")
		nomfic = self.get_name_of_current_season_config_file()
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
		if not isinstance(season, numbers.Number):
			raise TypeError(season)
		return os.path.join(self.manager.get_path_to_season(self.nom, season), \
				self.manager.config_file_season_name)

	def get_name_of_serie_config_file(self):
		return os.path.join(self.manager.get_path_to_serie(self.nom), \
				self.manager.config_file_serie_name)

	def get_path_to_serie(self):
		return self.manager.get_path_to_serie(self.nom)

	def get_name_of_current_season_config_file(self):
		return os.path.join(
				self.manager.get_path_to_season(self.nom, 
					self.num_saison), 
				self.manager.config_file_season_name)

	def get_path_to_current_season(self):
		return self.manager.get_path_to_season(self.nom, 
				self.num_saison)

	def get_path_to_season(self, season):
		return self.manager.get_path_to_season(self.nom, season)

	#def get_path_to_season(self, episode):
	#	return 

	def get_subtitle_list(self):
		return self.manager.get_subtitle_candidates(self.nom, \
				self.num_saison, self.num_episode)

	def get_video_list(self):
		return self.manager.get_video_candidates(self.nom, \
				self.num_saison, self.num_episode)

	def get_absolute_filename(self, filename):
		return os.path.join(self.manager\
				.get_path_to_season(self.nom, self.num_saison), \
				filename)

	def save_current_episode_parameters(self):
		pass	

class BashManagedSerieFactory:
	def __init__(self, manager):
		self.manager = manager

	def create_serie(self, name):
		return BashManagedSerie(name, self.manager)
	
	def create_serie_manager(self):
		return BashManagedSeriesData(self.manager, self)


class SeriesData(object):
	def __init__(self, current_serie, series):
		self.series = {}
		self.current_serie_name = current_serie
	
		for serie in series :
			print("Creating ", serie)
			self.series[serie] = None
		# self.series[currentSerie]= Serie(currentSerie)

		self.current_serie = self.series[current_serie]

	def set_current_serie_by_name(self, serie):
		self.current_serie_name = serie

		if self.series[serie] == None:
			self.add_serie(serie)
		
		self.current_serie = self.series[serie]
	
	def get_current_serie(self):
		self.set_current_serie_by_name(self.current_serie_name)
		return self.current_serie

	def add_serie(self, name):
		"""Stupid test function to delete """
		debug("pappy adding serie {}".format(name))
	
class BashManagedSeriesData(SeriesData):
	""" Serie info retrieved by bash scripts, historical"""
	def __init__(self, manager, serie_factory = None):
		SeriesData.__init__(self)
		self.manager = manager
		self.serie_factory = serie_factory
		if not self.serie_factory:
			self.serie_factory = BashManagedSerieFactory(manager)
		
		liste = manager.get_serie_list()
		super(BashManagedSeriesData, self)\
				.__init__(manager.get_current_serie(), liste)

	def get_base_path(self):
		return self.manager.get_absolute_path()
	
	def add_serie(self, name):
		info("fifis adding serie")
		self.series[name] = self.serie_factory.create_serie(name)


