#encoding: utf-8

""" utilies for unittesting """

from serie.bash_store import \
		ConfigManager, BashManagedSerie, BashManagedEpisode, \
		BashManagedSeason
from serie.serie_manager import SeriesManager

from utils.cli import CommandExecuter, CommandLineGenerator

import os

class DummySeriesManager(SeriesManager):

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
		SeriesManager.__init__(self)
		self.executer = None #command_executer()

# paths generator
	def get_global_config_file(self):
		return os.path.expanduser(self.config_file_abs_name)

	def get_absolute_path(self):
		return os.path.join(os.getcwd(), "_tmp")

	def get_path_to_serie(self, nom):
		return os.path.join(os.getcwd(), "_tmp", nom)

	def get_path_to_current_season(self):
		return os.path.join(self.get_path_to_serie(), "saison6")

	def get_path_to_current_season_of(self, name):
		return os.path.join(self.get_absolute_path(), "Dexter", "saison6")
	
	def get_path_to_season(self, nom, numsaison):
		return os.path.join(self.get_absolute_path(), "Dexter", "saison6")

	
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
				self.get_path_to_season(nom, numsaison), var_name)


# useful data getters
	def get_current_serie(self):
		return "Dexter"

	def get_num_current_season(self, nom):
		return 6

	# @trace
	def get_serie_list(self):
		print("getting serie list")
		liste_en_chaine = CommandExecuter().get_list_output(["series", "-l"])

		print("got serie list")
		return liste_en_chaine

	def get_current_episode(self, nom_serie, num_saison):
		return 6

	def get_subtitle_candidates(self, nom_serie, num_saison, num_ep):
		return self.get_candidates(nom_serie, num_saison, num_ep, "-L")
	
	def get_video_candidates(self, nom_serie, num_saison, num_ep):
		return self.get_candidates(nom_serie, num_saison, num_ep, "-V")

	def get_candidates(self, nom_serie, num_saison, num_ep, option):
		path = self.get_path_to_season(nom_serie, num_saison)
		if os.path.exists(path):
			command_g = CommandLineGenerator("play")
			command_g.add_option_param("-e", unicode(num_ep))
			command_g.add_option_single(unicode(option))
			return self.executer.get_list_output(command_g.get_command(), cwd=path)
                
		else:
			return []


def get_serie_and_ep():
	serie_manager = DummySeriesManager()
	serie = BashManagedSerie("Dexter", serie_manager)
	season = BashManagedSeason(serie, 5)
	episode = BashManagedEpisode(serie, season, 1)

	return (serie, episode)

MAIN_FILE = """
NAME='{}'
BASE='.'
"""

EPISODE_FILE = """
MOTIF=''
CUR='{}'
GENERICTIME='0'
DECALAGESUB='0'
OPTIONS='-fs'
NEED_SUB='on'
SUBFPS=''
"""

SEASON_FILE = """
SEASON='{}'
"""

MAIN_CONF_FILE = ".play_season"


def create_fake_env(name, season, ep):
	season_rep="Season {}".format(season)

	# main config file
	with open(MAIN_CONF_FILE, 'w') as f:
		f.write(MAIN_FILE.format(name))

	season_path = os.path.join(".", name, season_rep)
	
	try :
		os.makedirs(season_path)
	except OSError:
		pass
	finally :
		pass

	with open(os.path.join(name, ".play_season"), "w") as f:
		f.write(SEASON_FILE.format(season))

	with open(os.path.join(season_path, ".play_conf"), "w") as f:
		f.write(EPISODE_FILE.format(ep))


