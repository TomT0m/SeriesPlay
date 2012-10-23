#! /usr/bin/python
#encoding: utf-8
""" Test service """
from twisted.trial import unittest

from app.service import PipeService
from utils.on_event_deferred import OnEventDeferred
from twisted.internet import defer
class TestPipeService(unittest.TestCase):
	""" Simple Testcase """
	def setUp(self):
		"""init"""
		self.service = None

	def test_start_and_stop(self):
		""" Simple testcase """
		self.service = PipeService("/bin/sh")
		wait_for_start = OnEventDeferred(self.service,"service_started")
		wait_for_stop = OnEventDeferred(self.service, "service_ended")
		self.service.start()

		def stop(res):
			""" Callback on service stopping """
			#print("stopping service")
			self.service.stop()
			return res
		dlist = defer.DeferredList([ wait_for_start.addCallback(stop), \
				wait_for_stop ])
		return dlist


