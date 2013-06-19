#encoding: utf-8

""" utilies for unittesting """

from serie.fs_store import \
		ConfigManager, FsManagedSerie, FsManagedEpisode, \
		FsManagedSeason
from app.controller import VideoFinderController, PlayEventManager, \
		ExternalPlayerHandler

from serie.serie_manager import SeriesStore, SeriesData
from serie.fs_store import FsSeriesStore, FsManagedSeriesData
from app.main_app import App, VideoFinderService
from twisted.internet import reactor
from utils.cli import CommandExecuter, CommandLineGenerator

from app.config import Config
import app
from snakeguice.modules import Module
import os

from datasource.episode_video_finder import BaseEpisodeVideoFinder
from datasource.play_subdl import EmptySubdownloader, Subdownloader
from snakeguice import Injector

from utils.factory import FactoryFactory

class DummySeriesStore(SeriesStore):
	""" Dummy serie store object, no real datas but should work as a duck"""
	config_file_season_name = ".play_conf"	
	config_file_serie_name = ".play_season"
	config_file_abs_name = "~/.config/.series_play"

	path_to_series_var = "BASE"
	play_current_episode_var = "CUR"
	skip_time_var = "GENERICTIME"
	decay_time_var = "DECALAGESUB"
	serie_name_var = "NAME"
	fps_var = "SUBFPS"

	#pylint: disable=W0231
	def __init__(self):
		self.executer = None #command_executer()

# paths generator
	def get_global_config_file(self):
		""" dummy """
		return os.path.expanduser(self.config_file_abs_name)

	def get_absolute_path(self):
		""" dummy """
		return os.path.join(os.getcwd(), "_tmp")

	def get_path_to_serie(self, nom):
		""" dummy """
		return os.path.join(os.getcwd(), "_tmp", nom)

	#pylint: disable=W0613
	def get_path_to_current_season_of(self, name):
		""" dummy """
		return os.path.join(self.get_absolute_path(), "Dexter", "saison6")
	
	#pylint: disable=W0613
	def get_path_to_season(self, nom, numsaison):
		""" dummy """
		return os.path.join(self.get_absolute_path(), "Dexter", "saison6")


# config management 
	def read_conf_var(self, config_file_path, var_name):
		""" dummy """
		return ConfigManager.read_conf_var(config_file_path, var_name)
	
	def write_conf_var(self, config_file_path, var_name, var_value):
		""" dummy """
		return ConfigManager.write_conf_var(config_file_path, var_name, var_value)
		
	def read_num_conf_var(self, config_file_path, var_name):
		""" dummy """
		return ConfigManager.read_num_conf_var(config_file_path, var_name)

	def get_conf_variable(self, nom, numsaison, var_name):
		""" dummy """
		return self.read_conf_var(self.get_path_to_season(nom, numsaison), var_name)

	def get_num_conf_variable(self, nom, numsaison, var_name):
		""" dummy """
		return self.read_num_conf_var(
				self.get_path_to_season(nom, numsaison), var_name)


# useful data getters
	def get_current_serie(self):
		""" dummy """
		return "Dexter"

	def get_num_current_season(self, nom):
		""" dummy """
		return 6

	# @trace
	def get_serie_list(self):
		""" dummy """
		print("getting serie list")
		liste_en_chaine = CommandExecuter().get_list_output(["series", "-l"])

		print("got serie list")
		return liste_en_chaine
	#pylint: disable=W0613
	def get_current_episode(self, nom_serie, num_saison):
		""" dummy """
		return 6

	def get_subtitle_candidates(self, nom_serie, num_saison, num_ep):
		""" dummy """
		return self.get_candidates(nom_serie, num_saison, num_ep, "-L")
	
	def get_video_candidates(self, nom_serie, num_saison, num_ep):
		""" dummy """
		return self.get_candidates(nom_serie, num_saison, num_ep, "-V")

	def get_candidates(self, nom_serie, num_saison, num_ep, option):
		""" dummy """
		path = self.get_path_to_season(nom_serie, num_saison)
		if os.path.exists(path):
			command_g = CommandLineGenerator("play")
			command_g.add_option_param("-e", unicode(num_ep))
			command_g.add_option_single(unicode(option))
			return self.executer.get_list_output(command_g.get_command(), cwd=path)
                
		else:
			return []


def get_serie_and_ep():
	""" Returns a functional fake serie initialized object"""
	serie_manager = DummySeriesStore()
	serie = FsManagedSerie("Dexter", serie_manager)
	season = FsManagedSeason(serie, 5)
	episode = FsManagedEpisode(serie, season, 1)

	return (serie, episode)

MAIN_FILE = """
NAME='{}'
BASE='{}'
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


def create_fake_env(name, season, cur_ep, direc = "."):
	""" Creates a fake season & episode rep"""
	season_rep = "Season {}".format(season)

	# main config file
	with open(MAIN_CONF_FILE, 'w') as conffil:
		conffil.write(MAIN_FILE.format(name, direc))

	season_path = os.path.join(".", name, season_rep)
	
	try :
		os.makedirs(season_path)
	except OSError:
		pass
	finally :
		pass

	with open(os.path.join(name, ".play_season"), "w") as conf:
		conf.write(SEASON_FILE.format(season))

	with open(os.path.join(season_path, ".play_conf"), "w") as conf:
		conf.write(EPISODE_FILE.format(cur_ep))


class DummyVideoFinder(BaseEpisodeVideoFinder):
	""" Testing class : do nothing """
	def add_video_finder(self, tapp, plop):
		""" dummy """
		pass

	def search_newep(self, epi):
		""" dummy too"""
		pass

class DummyPlayerHandler(object):
	""" Dummy """
	#pylint:disable=W0613
	def execute_play_command(self, controller, cmd, cwd = None):
		""" Justs waits then call end of play """
		reactor.callLater(0.1, controller.end_of_play)


class TestAppModule(Module):
	""" Test app module injection configuration"""
	def configure(self, binder):
		""" configure method"""
		binder.bind(Subdownloader, to=EmptySubdownloader)
		
		self.install(binder, FakeControllerModule())

		config = Config(MAIN_CONF_FILE)
		binder.bind(SeriesStore, to_instance = FsSeriesStore(MAIN_CONF_FILE))
		binder.bind(Config, to_instance = config)
		binder.bind(PlayEventManager, to = PlayEventManager)
		binder.bind(SeriesData, to = FsManagedSeriesData)
		binder.bind(VideoFinderService, to_instance = app.service.Service(None))

def create_app():
	""" Fake App factory function """
	inj = Injector(TestAppModule())

	return App(inj)

class FakeControllerModule(Module):
	""" Fake """
	def configure(self, binder):
		self.install(binder, TestFinderModule())
		binder.bind(VideoFinderController, to = VideoFinderController)
		binder.bind(ExternalPlayerHandler, to = DummyPlayerHandler)

class TestFinderModule(Module):
	""" Fake """
	def configure(self, binder):
		facto = FactoryFactory(DummyVideoFinder)
		binder.bind(FactoryFactory, to_instance = facto)

def print_app_status(mapp):
	""" App info printing """
	combo_box = mapp.getitem("SerieListCombo")
	print("Série : {}, S{}E{}".format( value(combo_box), mapp.selected_season(), mapp.selected_numep()))

def value(combo):
	""" Returns selected combo box value """
	return combo.get_model().get_value(combo.get_active_iter(), 0)

