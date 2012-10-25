#!/usr/bin/python
#encoding: utf-8
""" Serie manager and Series Testing """

# from twisted.trial import unittest
import unittest

from serie.bash_store import BashSeriesManager, BashManagedSerie, BashManagedSeriesData
import os
import re

from tests.common_test import create_fake_env, \
		MAIN_CONF_FILE


class TestBashManager(unittest.TestCase):
	""" Test case : bash serie manager """

	def setUp(self):
		create_fake_env('ZPlop', 2, 2)
		create_fake_env('Plop', 2, 2)

	def assert_equivalent_path(self, path1, path2):
		abs1 = os.path.abspath(path1)
		abs2 = os.path.abspath(path2)

		self.assertTrue(abs1 == abs2)


	def test_serie(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
		serie_list = bash_manager.get_serie_list()
		self.assertTrue(bash_manager.get_global_config_file() == MAIN_CONF_FILE)
		self.assertTrue("Plop" in serie_list)
		self.assertTrue("ZPlop" in serie_list)
		self.assertTrue(len(serie_list) == 2)
		
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


		pattern = bash_manager.get_glob_pattern(1, 1, ["srt"])

		self.assertTrue(re.search(pattern, 'Bidou s01e01.srt'))
		self.assertFalse(re.search(pattern, 'Bidou s01e01.plop'))
		self.assertTrue(re.search(pattern, 'Dexter - 1x01 - Dexter.720p.BluRay.BoB.en.srt'))


