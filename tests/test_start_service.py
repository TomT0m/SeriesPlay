#! /usr/bin/python
#encoding: utf-8

from twisted.trial import unittest

from gi.repository import GObject, DBus
#import dbus
#import dbus.service

from DBus.mainloop.glib import DBusGMainLoop

__service_name__ = "org.tomt0m.serieplay"
__service_objpath__ = "/org/tomt0m/serieplay"

# dbus.set_default_mainloop()

class MyDBUSService(DBus.service.Object):
	""" Dummy DBus service """
	def __init__(self):
		DBus.set_default_main_loop(GObject.MainLoop())
		bus_name = DBus.service.BusName(__service_name__, bus = DBus.SessionBus())
		DBus.service.Object.__init__(self, bus_name, __service_objpath__)
 
    
	@DBus.service.method(__service_name__)
	def hello(self):
		""" Dummy method """
		return "Hello,World!"



class ServiceStartingTester(unittest.TestCase):
	""" Test starting a server """

	# def setUp(self):

	def test_get_service(self):
		""" Test dbus connection """
		self.myservice = MyDBUSService()
		bus = dbus.SessionBus()
		self.myservice = bus.get_object(__service_name__, __service_objpath__)	
		hello = self.myservice.get_dbus_method('hello', __service_name__)

		self.assertTrue(hello == "Hello,World!")


