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
