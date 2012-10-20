#!/usr/bin/python
#encoding: utf-8
""" Serie manager and Series Testing """

# from twisted.trial import unittest
import unittest

from serie.bash_store import BashSeriesManager, BashManagedSerie, BashManagedSeriesData
import os
import re


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


class TestBashManager(unittest.TestCase):
	""" Test case : bash serie manager """

	def setUp(self):
		create_fake_env('Plop', 2, 2)
		print("setting up")

	def assert_equivalent_path(self, path1, path2):
		abs1 = os.path.abspath(path1)
		abs2 = os.path.abspath(path2)

		self.assertTrue(abs1 == abs2)


	def test_serie(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		serie_list = bash_manager.get_serie_list()
		self.assertTrue(bash_manager.get_global_config_file() == MAIN_CONF_FILE)
		self.assertTrue("Plop" in serie_list)

		serie_name = bash_manager.get_current_serie_name()
		self.assertTrue( serie_name == "Plop" )
		

	def test_conffile(self):
		name = 'Plop'
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		self.assertTrue(bash_manager.get_global_config_file() == MAIN_CONF_FILE)
		
		expected_path = "."
		got_path = bash_manager.get_absolute_path()

		self.assert_equivalent_path(got_path, expected_path)

		got_file = bash_manager.get_serie_configfile(name)
		expected_file = os.path.join(name, ".play_season")

		self.assert_equivalent_path(got_file, expected_file)
		return True

	def test_episode(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		datas = BashManagedSeriesData(bash_manager)
		
		serie = datas.get_current_serie()

		self.assertTrue(serie.name == "Plop")
		
		next_episode = serie.season.episode
		cur_episode = bash_manager.get_current_stored_episode(serie.name, 2)
		
		print("current episode stored {}".format(cur_episode))
		print("next ep number {}".format(next_episode.number))
	
		self.assertTrue(cur_episode == next_episode.number)
		self.assertTrue(cur_episode == 2)

	def test_manager(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		# datas = BashManagedSeriesData(bash_manager)
		got = bash_manager.get_path_to_season("Plop", 2)
		self.assert_equivalent_path(got, "Plop/Season 2")

	def test_change_serie(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		# bash_

	def test_pattern(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)

		pattern = bash_manager.get_glob_pattern(1, 1, ["avi", "flv"])
		self.assertTrue(re.search(pattern, 'Bidou s01e01.avi'))
		self.assertFalse(re.search(pattern, 'Bidou s02e01.avi'))
		self.assertTrue(re.search(pattern, 'Bidou s01e01.flv'))
		self.assertFalse(re.search(pattern, 'Bidou s01e01.plop'))
