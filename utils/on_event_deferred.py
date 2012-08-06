#! /usr/bin/env/python
#encoding:utf-8
""" Implemented a twisted defered which trigers on Glib events"""

from twisted.internet import defer
from gi.repository import GObject #pylint: disable=E0611
# import gi.pygtkcompat
# gi.pygtkcompat.enable()
from logging import debug

class OnEventDeferred(defer.Deferred, GObject.GObject):
	""" The OnEventDeferred
	callbacks on init @event argument on @obj Glib object
	"""
	def __init__(self, obj, event, *args):
		defer.Deferred.__init__(self)
		GObject.GObject.__init__(self)
		self.handlers_id = [obj.connect(event, self._emited, *args)]
		self.obj = obj

	def _emited(self, *args):
		""" Glib callback, to call on glib events watched """
		debug("OnEventDeferred : event catched")
		self.callback(*args)
		self._clean()

	def _err_emited(self, *args):
		""" Glib callback, to call on glib err events """
		debug("OnEventDeferred : err event catched")
		self.errback(*args)
		self._clean()

	def add_error_event(self, obj, event, *args):
		""" Add event on obj which will trigger 
		error on this Deferred"""
		hid = obj.connect(event, self._err_emited, *args)	
		self.handlers_id.append(hid)

	def _clean(self):
		""" To call when trigerred """
		for hid in self.handlers_id:
			self.obj.handler_disconnect(hid)

