#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Module for managing Torrent Downloads : sending dl orders to deluge, ...
"""
from gi.repository import GObject # pylint: disable=E0611
import gi.pygtkcompat

from logging import info, debug

gi.pygtkcompat.enable()

from deluge.ui.client import client
# from twisted.internet import gtk2reactor#as reactor
from twisted.internet import reactor, defer

from deluge.log import setupLogger
setupLogger()


class DlAdder(GObject.GObject):
	""" Base class for defining Dl_adders : must define add_magnet
	"""
	__gsignals__ = {
		'connected':(GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
		'connect-fail':(GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
		'torrent-added':(GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,())
	}
	def add_magnet(self, magnet, destination):
		""" stub function : 
			@magnet : string
			@destination : path
			
		"""
		pass
		
		#GObject.Gobject.__init__(self)
		#GObject.signal_new("connected",dl_adder)

	def __init__(self):
		GObject.GObject.__init__(self)

class DelugeDlAdder(DlAdder):
	"""
		Class for adding a download with deluge
	"""
	def __init__(self, host="127.0.0.1", port=58846):
		DlAdder.__init__(self)
		self.port = port
		self.host = host
		self.defered_obj = None

	def connect(self):
		"""
		Connects with deluge server
		@returns a defered obj wich triggers when connected
		"""
		info("connect host={}, port={}".format(self.host, self.port))
		if self.host == None:
			self.defered_obj = client.connect()
		elif self.port != None:
			self.defered_obj = client.connect(port=self.port, host=self.host)
		else:
			self.defered_obj = client.connect(host=self.host)
		info("connecting request")	
		return self.defered_obj
		# self.defered_obj.addCallback(self.make_magnet_callback(".") )

	def on_connect_success(self, result):
		""" callback when connection is successful
		"""
		info("connection was succesful!")
		debug("result:{}".format(result))
		def on_get_config_value(value, key):
			""" Callbacks when config value got
			"""
			print "Got config value from the deamon :"
			print u"{0}: {1}".format(key, value)
			return True
		self.emit("connected") #pylint: disable=E1101
		client.core.get_config_value("download_location")\
				.addCallback(on_get_config_value, "download_location")

	def on_connect_fail(self, result):
		""" Error callback
		do nothing but stop reactor
		"""
		info("Connection failed!")
		debug("result: {]".format(result))
		self.emit("connect-fail") #pylint: disable=E1101
		reactor.stop() #pylint: disable=E1101
	
	def launch_command_order(self, magnet_link, dl_directory):
		""" Callback which launches the dl order to deluge
		"""
		def add_magnet(res):
			""" 
			The callback which ultimately lauches the order
			"""
			debug("calling magnet callback")
			options = {"move_completed": True,
				   "move_completed_path":dl_directory}
			print "result of connection {}".format(res)
			id_magnet = client.core.add_torrent_magnet(magnet_link, options)
			
			debug("id mag:{}, link::{}\n, options:{}"
					.format(id_magnet, magnet_link, options))
			return id_magnet

		print ("making magnet callback")
		return add_magnet

		
	def add_magnet(self, magnet_link, dl_directory):
		"""
		method wich try to add a download in deluge
		"""
		print "try adding magnet"
		defe = self.connect()
		deferred_launch_order = defer.Deferred()
		def on_command_sent(result):
			""" Callback when command is send, triggers
			launch order defered.
			TODO: checks for necessity, obsolete ?
			"""
			debug("-->calling command sent")
			deferred_launch_order.callback(result)
			debug("supposed to have triggered")
			return True

		def on_error_sent(err):
			""" Error callback when magnet addition"""
			info("--> calling command sent -->error !!! <{0}>".format(err))
			deferred_launch_order.errback(err)
			return False

		def on_connected(res):
			""" Deluge connected callback """
			info("connected to deluge")
			order_callback = self.launch_command_order(magnet_link, dl_directory)
			print order_callback
			res = order_callback(res)\
					.addCallback(on_command_sent)\
					.addErrback(on_error_sent)
			return True 
	
		defe.addCallback(on_connected).addErrback(deferred_launch_order.errback) 
		return deferred_launch_order

	def cleanup(self, result=None):
		""" cleanup callback """
		debug ("cleanup launched, result = {}".format(result))
		return client.disconnect()

	def wait_for_cleaning(self):
		""" returns the disconnection defered"""
		defered_disconnection = self.cleanup()
		return defered_disconnection
		
	def success(self, defered_added_result):
		""" Callback on successful addition """
		defered_added_result.addCallback(self.cleanup)
		info("success dl addition: result {}", defered_added_result)

	

def main():
	""" Test module function, obsolete """
	magnet_link = "magnet:?xt=urn:btih:038afcbf064655596d0500af2b74ebddf731bd5d&d\
n=Dirty+Sexy+Money+S02E07+The+Summer+House+HDTV+XviD-FQM+%5Be\
zt\
v%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A\
%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole\
.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80"
	plop = DelugeDlAdder(host="localhost")
	connection_waiter = plop.connect()
	connection_waiter.addCallback( plop.launch_command_order(magnet_link,".") )
	connection_waiter.addCallback(lambda x: info("cmmand launched !!"))\
			.addCallback(reactor.stop) #pylint: disable=E1101
	
	reactor.run()#pylint: disable=E1101


if __name__ == "__main__":
	main()

