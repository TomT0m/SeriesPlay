#!/usr/bin/python
#encoding:utf-8
""" subtitle management class """

from gi.repository import Gtk #pylint: disable=E0611
import os
from pysrt import SubRipFile#, SubRipItem, SubRipTime

from logging import info, debug

class subtitles_store:
	"""
	GTK Store for showing subtitles into the UI
	"""
	def __init__(self, filename):
		self.filename = filename
			
		self.model = Gtk.ListStore(object, str)
		self.srtModel = []
		if not os.path.exists(filename) :
			raise(FileNameError(filename))

		try:
			self.srtModel = SubRipFile.open(path=filename)
		except UnicodeDecodeError as unic:
			debug(unic)
			try:
				info("trying ...", "ISO-8859-1")
				self.srtModel = SubRipFile(path = filename, encoding = "iso-8859-1")
			except Exception as excep :
				debug(excep)
				self.model = None
		except IOError as error:
			info("Impossible de lire le fichier de sous titre: error {}".format(error))

		for line in self.srtModel:
			# print("appending",line)
			self.model.append([line, line.text])

	def get_model(self):
		""" getter for Model """
		return self.model


