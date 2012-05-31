#! /usr/bin/python
# -*- coding: utf8 -*-

#from future import

from gi.repository import GObject
import gi.pygtkcompat

gi.pygtkcompat.enable()

from deluge.ui.client import client
# from twisted.internet import gtk2reactor#as reactor
from twisted.internet import reactor,defer

from deluge.log import setupLogger
setupLogger()


class dl_adder(GObject.GObject):
	__gsignals__= {
		'connected':(GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
		'connect-fail':(GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
		'torrent-added':(GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,())
	}
	def add_magnet(self,magnet,destination):
		GObject.Gobject.__init__(self)
		GObject.signal_new("connected",dl_adder)
		pass

class deluge_dl_adder(dl_adder):
	def __init__(self,host="127.0.0.1",port=58846):
		dl_adder.__init__(self)
		self.port=port
		self.host=host
		pass

	def connect(self):
		print "connect host={}, port={}".format(self.host,self.port)
		if self.host == None:
			self.defered_obj=client.connect()
		elif self.port != None:
			self.defered_obj=client.connect(port=self.port,host=self.host)
		else:
			self.defered_obj = client.connect(host=self.host)
		print "connecting request"	
		return self.defered_obj
		# self.defered_obj.addCallback(self.make_magnet_callback(".") )

	def on_connect_success(self,result):
		print "connection was succesful!"
		print "result:",result
		def on_get_config_value(value,key):
			print "Got config value from the deamon :"
			print u"{0}: {1}".format(key,value)
			return True
		self.emit("connected")
		print "installing config value callback ..."
		client.core.get_config_value("download_location").addCallback(on_get_config_value,"download_location")

	def on_connect_fail(self,result):
	    print "Connection failed!"
	    print "result:", result
	    self.emit("connect-fail")
	    reactor.stop()
	
	def launch_command_order(self, magnet_link, dl_directory):
		def add_magnet(res):
			print "calling magnet callback"
			options = {"move_completed": True,
				   "move_completed_path":dl_directory}
			print "result of connection {}".format(res)
			id_magnet = client.core.add_torrent_magnet(magnet_link,options)
			
			print (id_magnet,magnet_link,options)
			return id_magnet

		print ("making magnet callback")
		return add_magnet

 

	def emit_sended_command(self):
		print "command sended"

	def command_error(self,error):
		print "there was an error : {}".format(error)
		return None
		
	def add_magnet(self,magnet_link, dl_directory):
		print "try adding magnet"
		defe = self.connect()
		deferred_launch_order = defer.Deferred()
		def on_command_sent(result):
			print "-->calling command sent"
			deferred_launch_order.callback(result)
			print "supposed to have triggered"
			return True

		def on_error_sent(result,err):
			print "--> calling command sent -->error !!!"
			deferred_launch_order.errback(res)
			print(err)
			return False

		def on_connected(res):
			print "connected"
			order_callback = self.launch_command_order(magnet_link,dl_directory)
			print order_callback
			res = order_callback(res).addCallback(on_command_sent).addErrback(on_error_sent)
			return True 
	
		defe.addCallback(on_connected).addErrback(deferred_launch_order.errback) 
		return deferred_launch_order

	def cleanup(self,result=None):
		print "cleanup launched"
		return client.disconnect()

	def wait_for_cleaning(self):
		defe=self.cleanup()
		
	def success(self,defered_added_result):
		defered_added_result.addCallback(self.cleanup)
		#defered_added_result.addCallback()
		#cal
		print "success !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

	

if __name__=="__main__":
	
	magnet_link="magnet:?xt=urn:btih:038afcbf064655596d0500af2b74ebddf731bd5d&dn=Dirty+Sexy+Money+S02E07+The+Summer+House+HDTV+XviD-FQM+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80"
	plop = deluge_dl_adder(host="localhost")
	c = plop.connect()
	# c.addCallback(plop.on_connect_success).addErrback(reactor.stop).addCallback(reactor.stop)
	c.addCallback( plop.launch_command_order(magnet_link,".") )
	c.addCallback(lambda x: sys.out.println("cmmand launched !!")).addCallback(reactor.stop) # addCallback(reactor.stop)
	reactor.run()

