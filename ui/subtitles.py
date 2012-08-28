#!/usr/bin/python
#encoding:utf-8
""" subtitle management class """

from gi.repository import Gtk #pylint: disable=E0611
import re, os
from pysrt import SubRipFile#, SubRipItem, SubRipTime

from logging import info, debug

class SubtitlesStore:
	"""
	GTK Store for showing subtitles into the UI
	"""
	def __init__(self, filename):
		self.filename = filename
			
		self.model = Gtk.ListStore(object, str)
		self.srt_model = []
		if not os.path.exists(filename) :
			raise(FileNameError(filename))

		try:
			self.srt_model = SubRipFile.open(path=filename)
		except UnicodeDecodeError as unic:
			debug(unic)
			try:
				info("trying ...", "ISO-8859-1")
				self.srt_model = SubRipFile(path = filename, encoding = "iso-8859-1")
			except Exception as excep :
				debug(excep)
				self.model = None
		except IOError as error:
			info("Impossible de lire le fichier de sous titre: error {}".format(error))

		for line in self.srt_model:
			# print("appending",line)
			self.model.append([line, line.text])

	def get_model(self):
		""" getter for Model """
		return self.model


def subtitle_comparison_function(model,           #pylint: disable=W0613
		column, key, ite, unknown = None):#pylint: disable=W0613
	""" returns True if string is in subtitle"""
	text = model.get_value(iter, 0).text.lower()
	if(re.match(r".*"+key, text, re.IGNORECASE)):
		return False
	return True

def started_search(treeview):#pylint: disable=W0613
	""" useless function, to delete ?"""
	debug ("search started")
	
def subtitle_line_text_getter(column,             #pylint: disable=W0613
		cell, model, ite, unknown = None):#pylint: disable=W0613
	""" Gets the text to show in corresponding column"""
	cell.set_property('text', model.get_value(iter, 0).text)
	return 	

def subtitle_begin_time_getter(column,            #pylint: disable=W0613
		cell, model, ite, unknown = None):#pylint: disable=W0613
	""" Gets the time to show in corresponding column"""
	cell.set_property('text', unicode(model.get_value(ite, 0).start))
	return
