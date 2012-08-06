#!/usr/bin/python
#encoding: utf-8
""" Helper Gtk ui functions """

from gi.repository import Gtk#pylint: disable=E0611
import logging

def populate_combo_with_items(combo, items):
	""" adds a list of items to a Gtk combo,
	replaces it if not empty
	"""
	list_store = None
	if combo.get_model() != None:
		list_store = combo.get_model()
		list_store.clear()
	else:
		list_store = Gtk.ListStore(str)
		cellr = Gtk.CellRendererText()
		combo.set_model(list_store)	
		combo.pack_start(cellr, True)
		combo.add_attribute(cellr, 'text', 0)
		combo.set_active(0)
	
	for i in items:
		logging.info("populating with {0}".format(i)) 
		list_store.append([str(i)])

	combo.set_active(0)
	return combo

