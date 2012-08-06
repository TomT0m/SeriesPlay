#! /usr/bin/python
#encoding: utf-8

from twisted.trial import unittest

from gi.repository import Gtk
import dbus
import dbus.service

from dbus.mainloop.glib import DBusGMainLoop

service_name = "org.tomt0m.serieplay"
service_objpath = "/org/tomt0m/serieplay"

# dbus.set_default_mainloop()

class MyDBUSService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(service_name, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, service_objpath)
 
    @dbus.service.method(service_name)
    def hello(self):
        return "Hello,World!"



class service_starting_tester(unittest.TestCase):
	def setUp(self):
		self.myservice = MyDBUSService()

	def testGetService(self):
		bus = dbus.SessionBus()
		self.myservice = bus.get_object(service_name,service_objpath)	
		hello = self.myservice.get_dbus_method('hello',service_name)

		self.assertTrue(hello == "Hello,World!")


