#!/usr/bin/python
#encoding:utf-8

from gi.repository import Gtk
import os
from pysrt import SubRipFile, SubRipItem, SubRipTime


class subtitles_store:
	"""
	GTK Store for showing subtitles into the UI
	"""
	def __init__(self,filename):
		self.filename=filename
			
		self.model=Gtk.ListStore(object,str)
		self.srtModel=[]
		if not os.path.exists(filename) :
			raise(FileNameError(filename))

		try:
			self.srtModel=SubRipFile.open(path=filename)
		except UnicodeDecodeError as unic:
			print(unic)
			try:
				print("trying ..." ,"ISO-8859-1")
				self.srtModel=SubRipFile(path=filename,encoding="iso-8859-1")
			except Exception as e :
				print(e)
				self.model=None
		except IOError as error:
			print("Impossible de lire le fichier de sous titre")

		for line in self.srtModel:
			# print("appending",line)
			self.model.append([line,line.text])

	def get_model(self):
		return self.model


