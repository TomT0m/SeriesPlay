#! /usr/bin/python
#encoding: utf-8
"""
External service management

Content :
* an interface to implement for different kind of services
	Currently handles GObject signals to be able to know when service is started 
	and stopped

* implemented by :
	* PipeService : an external subprocess spawned by current one

"""
from gi.repository import GObject #pylint: disable=E0611
from utils.on_event_deferred import OnEventDeferred
from twisted.internet import reactor

from logging import info

def async_start(service, dic, key):
	""" Puts service in dictionary in deferred start mode, 
	and replaces it on service started
	"""
	def on_started_replace(res):
		""" Replaces deferred with real service """
		dic[key] = service
	
	on_service_started = OnEventDeferred(service, "service_started")\
			.addCallback(on_started_replace)
	
	dic[key] = on_service_started
	
	service.start()
	
	return on_service_started


class Service(GObject.GObject):
	""" Service interface
	* signals : when service are started and stopped
	"""
	__gsignals__ = {
		'service_started' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
		'service_ended' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
        }
	def __init__(self, path):
		GObject.GObject.__init__(self)
		self.path = path

	def start(self):
		""" To implement : request service starting """
		pass

	def stop(self):
		""" To implement : request service stopping """
		pass

import subprocess
from time import sleep

class PipeService(Service):
	""" Implementation of Service.
	dummy :
	just starts a pipe and sends "service started"
	"""



	def __init__(self, path):
		Service.__init__(self, path)
		self.pipe = None
	
	def start(self):
		""" Start the process"""
		self.pipe = subprocess.Popen(
				self.path,
				shell = False,
				stdout = None,
				stdin = None)

		def started_callback():
			""" callbacks 1 second later """
			#pylint: disable=E1101
			self.emit("service_started")
		
		reactor.callLater(1, started_callback)
		

	def stop(self):
		""" Request service stopping"""
		self.pipe.terminate()
		self.pipe.kill()
		self.pipe.communicate()
		self.emit("service_ended")#pylint: disable=E1101


