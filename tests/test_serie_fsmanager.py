#!/usr/bin/python
#encoding: utf-8
""" Serie manager and Series Testing """

import unittest

from serie.fs_store import FsSeriesStore, \
		FsManagedSeriesData
from serie.serie_manager import SeriesData

import os
import re

from tests.common_test import create_fake_env, \
		MAIN_CONF_FILE

from snakeguice.modules import Module
from snakeguice import Injector
from serie.serie_manager import SeriesStore



class TestFsStore(unittest.TestCase):
	""" Test case : bash serie manager """
	cwd = None 

	def get_global_conffifile_fullpath(self):
		""" getting test configfile fullpath """
		return os.path.join(self.cwd, MAIN_CONF_FILE)

	def build_module(self):
		""" create a test module"""
		class FSSerieModule(Module):
			""" Serie object test module"""
			def configure(self_, binder):
				""" bindings """
				store = FsSeriesStore(self.get_global_conffifile_fullpath())
				binder.bind(SeriesStore, to_instance = store)
				binder.bind(SeriesData, to = FsManagedSeriesData)

		return FSSerieModule()

	def setUp(self):
		if self.cwd == None:
			TestFsStore.cwd = os.getcwd()
		os.chdir(self.cwd)
		create_fake_env('ZPlop', 2, 2, self.cwd)
		create_fake_env('Plop', 2, 2, self.cwd)
		try :
			os.mkdir('Plop/Season 2/s2e02/')
		except Exception:
			pass
		with open('Plop/Season 2/s2e02/S02E02.avi', "w") as fil:
			fil.write("bidou")

		os.chdir("/")

	def tearDown(self):
		os.chdir(self.cwd)

	def assert_equivalent_path(self, path1, path2):
		""" assertion definition """
		abs1 = os.path.abspath(path1)
		abs2 = os.path.abspath(path2)

		self.assertTrue(abs1 == abs2)


	def test_serie(self):
		""" testing serie object """
		bash_manager = FsSeriesStore(self.get_global_conffifile_fullpath())
		serie_list = bash_manager.get_serie_list()
		self.assertTrue(bash_manager.get_global_config_file() == 
				self.get_global_conffifile_fullpath())
		self.assertTrue("Plop" in serie_list)
		self.assertTrue("ZPlop" in serie_list)
		self.assertTrue(len(serie_list) == 2)
		
		serie_name = bash_manager.get_current_serie_name()
		self.assertTrue( serie_name == "Plop" )
		

	def test_conffile(self):
		""" testing test environment """
		name = 'Plop'
		bash_manager = FsSeriesStore(self.get_global_conffifile_fullpath())
		self.assertTrue(bash_manager.get_global_config_file() 
				== self.get_global_conffifile_fullpath())
		
		expected_path = self.cwd # "."
		got_path = bash_manager.get_absolute_path()
		self.assert_equivalent_path(got_path, expected_path)

		got_file = bash_manager.get_serie_configfile(name)
		expected_file = os.path.join(self.cwd, os.path.join(name, ".play_season"))

		self.assert_equivalent_path(got_file, expected_file)
		return True

	def test_episode(self):
		""" testing episode object """
		injector = Injector(self.build_module())
		
		datas = injector.get_instance(SeriesData)
		serie = datas.current_serie
		store = injector.get_instance(SeriesStore)
		
		self.assertTrue(serie.name == "Plop")
		
		next_episode = serie.season.episode
		cur_episode = store.get_current_stored_episode(serie.name, 2)
	
		print("current episode stored {}".format(cur_episode))
		print("next ep number {}".format(next_episode.number))
	
		self.assertTrue(cur_episode == next_episode.number)
		self.assertTrue(cur_episode == 2)

		self.assertEquals(len( next_episode.get_video_list() ), 1)
		self.assertEquals(len( serie.get_video_list() ), 1)

	def test_manager(self):
		""" Test of manager : retrieving season path"""
		fs_store = FsSeriesStore(self.get_global_conffifile_fullpath())
		# datas = BashManagedSeriesData(bash_manager)
		got = fs_store.get_path_to_season("Plop", 2)
		self.assert_equivalent_path(got, os.path.join(self.cwd,"Plop/Season 2"))

	def test_change_serie(self):
		""" undone yet"""
		
		injector = Injector(self.build_module())
		series = injector.get_instance(SeriesData)
		
		
		series.current_serie = "ZPlop"
		self.assertTrue(series.current_serie.name == "ZPlop" )
		series.current_serie = "Plop"
		
		self.assertTrue(series.current_serie.name == "Plop" )


		series.current_serie.season.episode = 5

		self.assertEquals(series.current_serie.season.episode.number, 5)
		
		series.current_serie.season = 10

		self.assertEquals(series.current_serie.season.episode.number, 1)

		# print(series)

	def test_pattern(self):
		""" testing file searching pattern creation"""
		bash_manager = FsSeriesStore(self.get_global_conffifile_fullpath())

		pattern = bash_manager.get_glob_pattern(1, 1, ["avi", "flv"])
		print(pattern)
		re.compile(pattern)
		self.assertTrue(re.search(pattern, u'Bidou s1e01.avi'))
		self.assertTrue(re.search(pattern, u'Bidou s01e01.avi'))
		self.assertFalse(re.search(pattern, u'Bidou s02e01.avi'))
		self.assertTrue(re.search(pattern, u'Bidou s01e01.flv'))
		self.assertFalse(re.search(pattern, u'Bidou s01e01.plop'))


		pattern = bash_manager.get_glob_pattern(1, 1, ["srt"])

		self.assertTrue(re.search(pattern, u'Bidou s01e01.srt'))
		self.assertFalse(re.search(pattern, u'Bidou s01e01.plop'))
		self.assertTrue(re.search(pattern, 
			u'Dexter - 1x01 - Dexter.720p.BluRay.BoB.en.srt'))
		self.assertFalse(re.search(pattern, u'Bidou 1 and 1.avi'))

