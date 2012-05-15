#! /usr/bin/python
# -*- coding: utf8 -*-


from deluge.ui.client import client
from twisted.internet import gtk2reactor#as reactor
#gtk2reactor.install()
from twisted.internet import reactor

import gobject

from deluge.log import setupLogger
setupLogger()


class dl_adder(gobject.GObject):
	__gsignals__= {
		'connected':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,())
	}
	def add_magnet(self,magnet,destination):
		gobject.Gobject.__init__(self)
		gobject.signal_new("connected",dl_adder)
		pass

class deluge_dl_adder(dl_adder):
	def __init__(self):
		dl_adder.__init__(self)
		# self.connect()
		# client.connect(localhost,)
		pass

	def connect(self):
		self.defered_obj=client.connect()
		self.defered_obj.addCallback(self.on_connect_success)
		self.defered_obj.addErrback(self.on_connect_fail)


	def on_connect_success(self,result):
		print "connection was succesful!"
		print "result:",result
		def on_get_config_value(value,key):
			print "Got config value from the deamon :"
			print u"{0}: {1}".format(key,value)
			client.disconnect()
			reactor.stop()
			return True
		self.emit("connected")
		print "installing config value callback ..."
		client.core.get_config_value("download_location").addCallback(on_get_config_value,"download_location")

	def on_connect_fail(self,result):
	    print "Connection failed!"
	    print "result:", result
	    reactor.stop()


		
	
if __name__=="__main__":
	# d = client.connect()
	# d.addCallback(on_connect_success)
	# d.addErrback(on_connect_fail)
	plop = deluge_dl_adder()
	plop.connect()
	reactor.run()

