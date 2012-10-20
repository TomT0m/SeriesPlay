#!/usr/bin/python
#encoding:utf-8


import unittest

from utils.cli import ConfigManager

SAMPLE_FILE="""
PLOP='1'
BIDOU="2"
NOM='Dex\' and Friends'

"""

class TestConfigReader(unittest.TestCase):
	def setUp(self):
		with open("plop", 'w') as f:
			f.write(SAMPLE_FILE)

	
	def testReader(self):
		tested = ConfigManager("plop")

		self.assertTrue(tested.read_num_var('PLOP') == 1)
		self.assertTrue(tested.read_num_var('BIDOU') == 2)
		nom = tested.read_var('NOM')
		self.assertTrue(nom == "Dex' and Friends")
		

