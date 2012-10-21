#! /usr/bin/python
#encoding: utf-8

from twisted.trial import unittest

from gi.repository import GObject, DBus
#import dbus
#import dbus.service

# from DBus.mainloop.glib import DBusGMainLoop

__service_name__ = "org.tomt0m.serieplay"
__service_objpath__ = "/org/tomt0m/serieplay"

# dbus.set_default_mainloop()

class _Gio_DBusMethodInfo:
	interface = None
    	in_args = None
	out_signature = None

def Gio_bus_method(dbus_interface, in_signature=None, out_signature=None):
	def decorator(func):
		func._dbus_method = _Gio_DBusMethodInfo()
		func._dbus_method.interface = dbus_interface
        	func._dbus_method.out_signature = out_signature or ''
        	func._dbus_method.in_args = []
		in_signature_list = GLib.Variant.split_signature(in_signature)
		arg_names = inspect.getargspec(func).args
		arg_names.pop(0) # eat "self" argument
		if len(in_signature) != len(arg_names):
			raise TypeError, 'specified signature %s for method %s does not match length of arguments' % (str(in_signature_list), func.func_name)
		for pair in zip(in_signature_list, arg_names):
			func._dbus_method.in_args.append(pair)
		return func
	return decorator



#class MyDBUSService(DBus.service.Object):
#	""" Dummy DBus service """
#	def __init__(self):
#		DBus.set_default_main_loop(GObject.MainLoop())
#		bus_name = DBus.service.BusName(__service_name__, bus = DBus.SessionBus())
#		DBus.service.Object.__init__(self, bus_name, __service_objpath__)
#	@DBus.service.method(__service_name__)
#	def hello(self):
#		""" Dummy method """
#		return "Hello,World!"



class ServiceStartingTester(unittest.TestCase):
	""" Test starting a server """

	def setUp(self):
		pass

	def test_get_service(self):
		""" Test dbus connection """
		self.myservice = MyDBUSService()
		bus = dbus.SessionBus()
		self.myservice = bus.get_object(__service_name__, __service_objpath__)	
		hello = self.myservice.get_dbus_method('hello', __service_name__)

		self.assertTrue(hello == "Hello,World!")
	test_get_service.skip="désactive temporairement" 

	def test_setup(self):
		return True
