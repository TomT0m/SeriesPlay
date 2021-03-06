#!/usr/bin/python
#encoding:utf-8
""" Model for a Result list view 
( magnets + files info together )"""

from gi.repository import Gtk#pylint: disable=E0611

class VideoResultStore(object):
	"""GTK store for video candidates results
	"""
	def __init__(self, candidates, model = None):
		self.candidates = candidates
		if not model:
			self.model = Gtk.ListStore(object, str)
		else:
			self.model = model

		for candidate in candidates:
			self.model.append([candidate, candidate.filename])

	def get_model(self):
		""" Model getter """
		return self.model


def filename_text_getter(column, cell, model, itera, unknown = None):\
		#pylint: disable=W0613
	""" Data getter function for the filename column"""
	# print model
	# print 'getter called'
	# print column
	# import pdb ; pdb.set_trace()
	cell.set_property('text', model.get_value(itera, 0).filename)

def leechers_text_getter(column, cell, model, itera, unknown = None):\
		#pylint: disable=W0613
	""" Data getter function for the llechers numbers column"""
	value = model.get_value(itera, 0).leechers
	cell.set_property('markup', "<i>{}</i>".format(value))
	
def filesize_text_getter(column, cell, model, itera, unknown=None):\
		#pylint: disable=W0613
	""" Data getter function for the filesize column"""
	value = model.get_value(itera, 0).filesize
	cell.set_property('text', u"{}".format(value))

def init_torrentlist_viewer(viewer):
	"""function setting up the torrent choices view
		@param : viewer, the Tree View
	"""
	
	# filename rendering
	cellpbtext = Gtk.CellRendererText()
	filename = Gtk.TreeViewColumn("Name", cellpbtext)
	
	filename.set_cell_data_func(cellpbtext, filename_text_getter)
	viewer.append_column(filename)

	# sources number rendering
	sources_renderer = Gtk.CellRendererText()
	sources_column = Gtk.TreeViewColumn("Sources", sources_renderer)
	sources_column.set_cell_data_func(sources_renderer, leechers_text_getter)

	viewer.append_column(sources_column)

	# filesize rendering
	filesize_renderer = Gtk.CellRendererText()
	filesize_column = Gtk.TreeViewColumn("Size", filesize_renderer)
	filesize_column.set_cell_data_func(filesize_renderer, filesize_text_getter)

	viewer.append_column(filesize_column)

