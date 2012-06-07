#! /usr/bin/env/python
#encoding:utf-8


from twisted.internet import defer
from gi.repository import GObject

# import gi.pygtkcompat
# gi.pygtkcompat.enable()

class OnEventDeferred(defer.Deferred,GObject.GObject):
	def __init__(self,obj,event,*args):
		defer.Deferred.__init__(self)
		GObject.GObject.__init__(self)
		self.handlers_id=[obj.connect(event,self.emited,*args)]

	def emited(self,*args):
		print "OnEventDeferred : event catched"
		self.callback(*args)
		self.clean()

	def err_emited(self,*args):
		print "OnEventDeferred : err event catched"
		self.errback(*args)
		self.clean()

	def add_error_event(self,obj,event,*args):
		hid = obj.connect(event,self.err_emited,*args)	
		self.handlers_id.append(hid)

	def clean(self):
		for id in self.handlers_id:
			obj.handler_disconnect(id)
