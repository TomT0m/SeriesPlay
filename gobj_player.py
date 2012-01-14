# encoding : utf-8

# import pygtk
import gobject
import pygtk
pygtk.require('2.0')
import gobject
import time 

from decorator import decorator

import mplayer_slave

class Car(gobject.GObject):
    __gproperties__ = {
        'fuel' : (gobject.TYPE_FLOAT, 'fuel of the car',
                  'amount of fuel that remains in the tank',
                  0, 60, 50, gobject.PARAM_READWRITE)
        }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.fuel = 50

    def do_get_property(self, property):
        if property.name == 'fuel':
            return self.fuel
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def do_set_property(self, property, value):
        if property.name == 'fuel':
            self.fuel = value
        else:
            raise AttributeError, 'unknown property %s' % property.name

gobject.type_register(Car)
def command_sender(func):
        def wrapper(*args,**kwargs):
                print("sending ... command {0}".format(func.__name__))
		try:
			print(func)
			print(args)
			result=func(*args,**kwargs)

		except IOError:
			args[0].player.__init__()
			args[0].emit('play_ended')
			result=None
		return result
	return wrapper 



class Player_status(gobject.GObject):
	__gproperties__ = { 
		'playing' : (	gobject.TYPE_BOOLEAN,                        # type
				'playing status',                         # nick name
				'true if currently playing', # description
				False,                                        # default value
				gobject.PARAM_READWRITE)                   # flags
	}
	__gsignals__ = {
		'player_restarted' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'play_ended' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}
	# gsignal('engine-started', float)


	@command_sender
	def update_status(self):
		print(self)
		self.get_current_time()
		pass

	def __init__(self,player=None):

		gobject.GObject.__init__(self)
		print("creating the slave mplayer")
		if player==None:
			self.player=mplayer_slave.player()
		else:
			self.player=player
		self.playing=False
		self.pause = False
		self.gstatusupdater=gobject.timeout_add(500, self.update_status)

	def do_get_property(self, property):
		if property.name == 'fuel':
			return self.fuel
		else:
			raise AttributeError, 'unknown property %s' % property.name
	def do_set_property(self,property,value):
		if property.name == 'fuel':
			self.fuel = value
		else:
			raise AttributeError, 'unknown property %s' % property.name
	@command_sender
	def set_playing(self):
		self.playing=True

	def get_playing(self):
		return self.playing

	def stop(self):
		if self.playing :
			self.playing=False
	
	def pause(self):
		if self.playing :
			# self.
			pass

	@command_sender
	def handle_seek(self,srt_time):
		seek_time=srt_time.to_time()
		print(seek_time)
		seek_seconds = seek_time.hour*3600+seek_time.minute*60 + seek_time.second+seek_time.microsecond*10e-7 - 2
		print(seek_seconds)
		self.player.seek(seek_seconds)

	@command_sender
	def get_current_time(self):
		
		return self.player.get_current_seconds()

	@command_sender
	def get_subtitles_delay(self):
		return self.player.get_subtitles_delay()

	@command_sender
	def set_subtitles_delay(self,absolutedelay):
		return self.player.set_subtitles_delay(absolutedelay)

	@command_sender
	def set_subtitles(self,subfile):
		return self.player.load_subtitle(subfile)

	@command_sender
	def play(self,filename):
		return self.player.play(filename)
	@command_sender
	def get_video_resolution(self):
		return self.player.get_video_resolution()

	def end_player(self):
		return self.player.end_player()

	#@command_sender
	#def wrapped_command(self, command, *args=None):
	#	try
	#		result=command(args)
	#	except IOError:
	#		self.emit('play_ended')

gobject.type_register(Player_status)


