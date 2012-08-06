#! /usr/bin/python
#encoding:utf-8

""" Testcases for MPlayer slave process python communicator class """


import os


__Sample_vid__url__ = \
"http://upload.wikimedia.org/wikipedia/commons/6/60/Polar_orbit.ogg"

__datadir__ = os.path.join("..","tests","data")
__VideoPath__ = os.path.join(__datadir__, "Polar_orbit.ogg")



from twisted.trial import unittest
# from twisted.internet import defer 
import twisted.web.client

from utils.cli import CommandExecuter, CommandLineGenerator

class MplayerSlaveTester(unittest.TestCase):
	""" Testcase for piloting a Slave Mplayer """	
	
	
	def setUp(self):
		""" Setting up : 
		* creation of a video file
		"""
		self.wait_for_end = None # defer.Deferred()

		print(__VideoPath__)
		if not os.path.exists(__VideoPath__):
			print("plop")
			try:
				os.makedirs(__datadir__) 
			except OSError as excep: # Python >2.5
				if excep.errno == os.errno.EEXIST:
					pass
				else: raise


			dl = twisted.web.client.downloadPage(__Sample_vid__url__, __VideoPath__)
			self.wait_for_end = dl
			print (os.getcwd())
			print(dl)
		
		return self.wait_for_end

	def test_video_play(self):
		""" Testing system mplayer presence """
		command = CommandLineGenerator("mplayer")
		command.add_option_single(__VideoPath__)
		CommandExecuter().get_output(command.get_command())
		return True

