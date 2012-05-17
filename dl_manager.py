#! /usr/bin/python
# -*- coding: utf8 -*-

#from future import

from deluge.ui.client import client,Client
from twisted.internet import gtk2reactor#as reactor
from twisted.internet import reactor

import gobject

from deluge.log import setupLogger
setupLogger()


class dl_adder(gobject.GObject):
	__gsignals__= {
		'connected':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
		'connect-fail':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
		'torrent-added':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,())
	}
	def add_magnet(self,magnet,destination):
		gobject.Gobject.__init__(self)
		gobject.signal_new("connected",dl_adder)
		pass

class deluge_dl_adder(dl_adder):
	def __init__(self,port=None):
		dl_adder.__init__(self)
		self.port=port
		pass

	def connect(self,port=None, host="localhost"):
		if port == None and self.port ==None:
			self.defered_obj=client.connect()
		elif port!=None:	
			self.defered_obj=client.connect(host=host,port=port)
		else:
			self.defered_obj=client.connect(port=self.port,host=host)
		#self.defered_obj.addCallback(self.on_connect_success)
		#self.defered_obj.addErrback(self.on_connect_fail)
		
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
			options = {"download_location":dl_directory}
			print "result of connection {}".format(res)
			id =  client.core.add_torrent_magnet(magnet_link,options)
			print (id,magnet_link,options)
			return id
		print ("making magnet callback")
		return add_magnet

 

	def emit_sended_command(self):
		print "command sended"

	def command_error(self,error):
		print "there was an error : {}".format(error)
		return None
		
	def add_magnet(self,magnet_link, dl_directory):
		defe = self.connect()
		def on_command_sent(result):
			print "-->calling command sent"
			defe.callback(result)
		def on_error_sent(result):
			print "--> calling command sent -->error !!!"
		def on_connected(result):
			print "\non connected : OK"
			defered_command=(self.launch_command_order(magnet_link,dl_directory)(result))
			print defered_command
			defered_command.addCallback(on_command_sent)
			defered_command.addErrback(on_error_sent)
			defered_command.addErrback(self.cleanup)
			print defered_command
			return True #defered_command

		#defe = self.connect()
		defe.addCallback(on_connected)
		return defe

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
	plop = deluge_dl_adder()
	c = plop.connect(host="localhost")
	# c.addCallback(plop.on_connect_success).addErrback(reactor.stop).addCallback(reactor.stop)
	c.addCallback( plop.launch_command_order(magnet_link,".") )
	c.addCallback(lambda x: sys.out.println("cmmand launched !!")) # addCallback(reactor.stop)
	reactor.run()

