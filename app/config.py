#! /usr/bin/python
#encoding: utf-8

"""
Sample configuration class

"""
from utils.cli import ConfigManager

import os

class Config:
	""" Class used to manage a configuration for SeriePlay """
	
	config_file_abs_name = os.path.expanduser("~/.play_season")
	
	def __init__(self, config_file = None):
		if config_file:
			self.reader = ConfigManager(config_file)
		else:
			self.reader = ConfigManager(self.config_file_abs_name)

	def get_sub_extensions(self):
		""" 
                Returns the subtiltle filename extensions searched, currently just .srt
                """
		return ["srt"] 

	def get_video_extensions(self):
		""" 
                Returns the video filename extensions searched, currently just .srt
                """
		return ["avi", "mp4", "mov"]

