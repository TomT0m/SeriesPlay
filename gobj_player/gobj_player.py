#! /usr/bin/python
#encoding: utf-8
""" GObject managing a slave process and 
miroring its state and state changes """

# from gi.repository import Gtk #pylint: disable=E0611
from gi.repository import GObject #pylint: disable=E0611

# import time 

from logging import debug, info

from decorator import decorator

from mplayer_slave import MPlayerSlave

# @decorator
def command_sender(func):
	""" decorator for catching and watching 
	state changes of slave, restarting in case of non answers
	"""
	def wrapper(self,*args, **kwargs):
		""" the real wrapper """ 
		try:
			result = func(self,*args, **kwargs)

		except IOError:
			args[0].player.__init__()
			args[0].emit('play_ended')
			result = None
		return result
	return wrapper 



class PlayerStatus(GObject.GObject):
	""" GObject handling managing a slave MPlayer object,
	syncing its status with internal mplayer process status
	"""
	__gproperties__ = { 
		'playing' : (	GObject.TYPE_BOOLEAN,                        # type
				'playing status',                         # nick name
				'true if currently playing', # description
				False,                                        # default value
				GObject.PARAM_READWRITE)                   # flags
	}
	__gsignals__ = {
		'player_restarted' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
		'play_ended' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
	}


	@command_sender
	def update_status(self):
		""" update the internal status
		TODO : develop """
		# print("updating status {0}".format(self.num_check))
		self.num_check = self.num_check+1
		if self.get_current_time()==False and self.get_playing():
			self.emit("play_ended") #pylint: disable=E1101
			self.stop()
		return True

	def __init__(self, player=None):
		self.num_check = 0
		GObject.GObject.__init__(self)
		info("creating the slave mplayer")
		if player == None:
			self.player = MPlayerSlave()
		else:
			self.player = player
		self.playing = False
		self.pause = False
		self.gstatusupdater = \
				GObject.timeout_add_seconds(2, 
						self.update_status)
		
#	def do_get_property(self, property):
#		if property.name == 'fuel':
#			return self.fuel
#		else:
#			raise AttributeError, 'unknown property %s' % property.name
#	def do_set_property(self,property,value):
#		if property.name == 'fuel':
#			self.fuel = value
#		else:
#			raise AttributeError, 'unknown property %s' % property.name
	@command_sender
	def set_playing(self):
		""" Setter for player, 
		should be unused for now """
		self.playing = True

	def get_playing(self):
		""" getter for status """ 
		return self.playing

	def stop(self):
		""" ??? unfinished """ 
		if self.playing :
			self.playing = False
	
	#def pause(self):
	#	if self.playing :
	#		# self.
	#		pass

	@command_sender
	def handle_seek(self, srt_time):
		""" seeks to a srt time 
		TODO: Debug this""" 
		seek_time = srt_time.to_time()
		debug(seek_time)
		seek_seconds = seek_time.hour * 3600 + \
				seek_time.minute * 60 + \
				seek_time.second + \
				seek_time.microsecond * 10e-7 - 2
		debug(seek_seconds)
		self.player.seek(seek_seconds)

	@command_sender
	def get_current_time(self):
		""" get current status where seeked """	
		return self.player.get_current_seconds()

	@command_sender
	def get_subtitles_delay(self):
		""" get delay of subtitle showed """
		return self.player.get_subtitles_delay()

	@command_sender
	def set_subtitles_delay(self, absolutedelay):
		""" Sets the subtiltle delay """ 
		return self.player.set_subtitles_delay(absolutedelay)

	@command_sender
	def set_subtitles(self, subfile):
		""" Sets the subtitles file """ 
		return self.player.load_subtitle(subfile)

	@command_sender
	def play(self, filename):
		""" Sets the file to play
		returns a True boolean if success, False otherwise
		"""
		if self.player.play(filename):
			self.set_playing()
			return True
		else:
			return False

	@command_sender
	def get_video_resolution(self):
		""" Returns a int * int couple """
		return self.player.get_video_resolution()

	def end_player(self):
		""" kills the player """ 
		return self.player.end_player()

# GObject.type_register(Player_status)

