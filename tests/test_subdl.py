#! /usr/bin/python
#encoding: utf-8


from twisted.trial import unittest

from datasource.play_subdl import TVsubtitlesSubdownloader
from tests.common_tests import create_fake_env

class TestTvsubdl(unittest.TestCase):

	def setUp(self):
		create_fake_env("Dexter", 1, 1)

	def test_dl(self):
		bash_manager = BashSeriesManager(MAIN_CONF_FILE)
	
	def test_search_and_dl(self):

		obj.get_for_ep("Dexter", 6, 12, "./dst")
		obj.get_for_ep("Treme", 1, 1, "./dst")

		self.assertTrue(os.path.exists())
