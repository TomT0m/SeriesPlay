#! /usr/bin/python
#encoding: utf-8


from twisted.trial import unittest
from serie.fs_store import FsSeriesStore

from datasource.play_subdl import TVsubtitlesSubdownloader
from tests.common_test import create_fake_env, MAIN_CONF_FILE

import os

class TestTvsubdl(unittest.TestCase):

	def setUp(self):
		create_fake_env("Dexter", 1, 1)

	def test_dl(self):
		bash_manager = FsSeriesStore(MAIN_CONF_FILE)
	
	def test_search_and_dl(self):
		obj = TVsubtitlesSubdownloader()
		
		obj.get_for_ep("Dexter", 6, 12, "./dst")
		obj.get_for_ep("Treme", 1, 1, "./dst")

		self.assertTrue(os.path.exists("./dst/Dexter - 6x12 - Electric Chair.HDTV.shafiullah.en.srt"))
