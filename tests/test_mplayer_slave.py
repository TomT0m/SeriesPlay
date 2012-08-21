#! /usr/bin/python
#encoding:utf-8

""" Testcases for MPlayer slave process python communicator class """


import os


# data dirs 

__Sample_vid__url__ = \
"http://upload.wikimedia.org/wikipedia/commons/6/60/Polar_orbit.ogg"

__datadir__ = os.path.join("..", "tests", "data")
__VideoPath__ = os.path.join(__datadir__, "Polar_orbit.ogg")



from twisted.trial import unittest
# from twisted.internet import defer 
import twisted.web.client

from utils.cli import CommandExecuter, CommandLineGenerator
from gobj_player import gobj_player, mplayer_slave


def get_subtitle( second ):
	""" Gets a sample subtitle srt string for @second """
	template = """
{0}
00:00:{0:2d},000 --> 00:00:{1:2d},230
{0} to {1}
"""
	return template.format(second, second+1) 

def get_subtitle_string( seconds ):
	""" constructs a sample "srt formated" string subtitles """
	subs = [get_subtitle(second) for second in range(0, seconds) ] 
	return ''.join(subs)

def get_video():
	""" downloads a sample video if none downloading"""
	wait_for_end = None # defer.Deferred()
	print(__VideoPath__)
	if not os.path.exists(__VideoPath__):
		print("plop")
		try:
			os.makedirs(__datadir__) 
		except OSError as excep: # Python >2.5
			if excep.errno == os.errno.EEXIST:
				pass
			else: raise


		wait_for_end = twisted.web.client\
				.downloadPage(__Sample_vid__url__, __VideoPath__)
	return wait_for_end

class MplayerSlaveTester(unittest.TestCase):
	""" Testcase for piloting a Slave Mplayer """	
	
	
	def setUp(self):
		""" Setting up : 
		* creation of a video file
		"""
				
		return get_video

	def test_video_play(self):
		""" Testing system mplayer presence """
		command = CommandLineGenerator("mplayer")
		command.add_option_single(__VideoPath__)
		CommandExecuter().get_output(command.get_command())
		return True

	def test_mplayer_slave(self):
		""" Tests for a slave mplayer launching """
		test_slave = mplayer_slave.MPlayerSlave()
		# test_slave.get_property("status")

		self.assertRaises(mplayer_slave.MPlayerSlave.PropertyUnknown, \
				test_slave.get_property, "status")

class GobjPlayerTester(unittest.TestCase):
	""" Testing the gobj_player object """
	def setUp(self):
		""" init """
		wait_for_video_get = get_video()
		return wait_for_video_get

	# def watch_propert()
	def test_creation(self):
		""" test of object creation  """
		status = gobj_player.PlayerStatus()
		status.end_player()

