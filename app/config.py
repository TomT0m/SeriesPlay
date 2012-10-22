#! /usr/bin/python
#encoding: utf-8

from utils.cli import ConfigManager


class Config:
	def __init__(self, config_file = None):
		if config_file:
			self.reader = ConfigManager(config_file)
		else:
			self.reader = ConfigManager(BashSerieManager.config_file_abs_name)

	def get_sub_extensions(self):
		return ["srt"] 

	def get_video_extensions(self):
		return ["avi", "mp4", "mov"]

