#encoding:utf-8
#! /usr/bin/python2.6
""" MPlayer slave management """

import utils.cli as cli
import subprocess

import select
import re

from logging import debug, info

class MPlayerSlave:
	""" a passive MPlayer process container.
	Communicates with it throw a pipe

	"""
	class PropertyUnknown(Exception):
		""" Communication with slave exception"""
		def __init__(self, msg):
			Exception.__init__(self, msg)	

	def __init__(self, vid=None):
		command = cli.command_line_generator("mplayer")
		command.add_option_single("-slave")
		command.add_option_single("-quiet")
		command.add_option_single("-idle")
		if vid != None:
			command.add_option_param("-wid", unicode(vid))
		
		info("Launching a new MPlayer")
		self.process = subprocess.Popen(command.get_command(), 
				shell = False, 
				stdin = subprocess.PIPE, 
				stdout = subprocess.PIPE, 
				stderr = subprocess.PIPE)
		self.process.poll()
		#print(self.process.poll())

	def launch(self, video_filepath, subfile_path=None):
		""" Launches a video (unimplemented)"""
		pass

	def send_command(self, command):
		""" Internal method : sends a MPlayer command string"""
		# self.process.stdin.flush()
		# print("sending command : \"{0}\"".format(command))
		# print ("lignes lues : ",self._readlines())
		self.process.stdin.write(command + "\n")
		#self.process.stdin.flush()
		#result = self._readlines()[0]

	def send_command_with_result(self, command):
		""" Sends a command to MPlayer, reads the output
		and returns the answer string to this command to the sender
		returns None if no answer
		"""
		self.send_command(command)
		result = []
		found = False
		while not found :
			result = self._readlines() 
			for line in result :
				# print ("analysing line '{0}'".format(x))
				# print  (x.find("ANS_"))
				if line.find("ANS_")==0:
					retour = line 
					found = True
					break

				if line.find("-1")==0:
					retour = None
					found = True

		# print ("yeah !!",retour)
		return retour

	def send_command_ignoring_results(self, command):
		""" Sends a command, 
		reads the answer but do nothing with it
		"""
		self.send_command(command)
		lines = self._readlines()
		debug(lines)
		#for x in lines :
			# print(x)

	def get_property(self, prop):
		""" Returns a "property" of MPlayer process value """
		debug("getting property", prop)
		
		result = self.send_command_with_result("get_property " + prop)
		#print("Mplayer result : '{0}'".format(result))
		if re.search("ANS_ERROR=PROPERTY_UNKNOWN", result):
			raise self.PropertyUnknown("Property unknown")

		if re.search("ANS_ERROR=PROPERTY_UNAVAILABLE", result):
			return False
		couple = re.match(r"ANS_"+prop+"=(\d+(\.\d+)?).*", result)
		# if couple:
		return couple.group(1)
		

	def get_current_seconds(self):
		""" Returns the current position in the video, in seconds """
			#ANS_TIME_POSITION=20.1
		res = self.get_property("time_pos")
		if res == False:
			return False
		else:
			return float(res)
		#res = self.send_command_with_result("get_property time_pos")
		#couple = re.match(r"ANS_TIME_POSITION=(\d+\.\d+).*", res)
		#print (couple)
		#return float(couple.group(1))

	def set_current_file(self, filename):
		""" Sets a new file to MPlayer to play (unimplemented)"""
		pass

	def end_player(self):
		""" Kills the player """
		self.process.kill()

	def play(self, filename) :
		""" Loads a new file """ 
		command = "loadfile \"{}\"".format(filename)
		self.send_command(command)

	def get_video_resolution(self):
		""" returns a int*int couple as width, 
		heigth of the videofile
		"""
		info("getting video resolution")
		#res = self.send_command_with_result("get_video_resolution")
		width = self.get_property("width")
		height = self.get_property("height")
		#couple = re.match(r"ANS_VIDEO_RESOLUTION='(\d+) x (\d+)'.*", res)
		# print couple 
		return int(width), int(height)

	def set_fullscreen(self):
		""" Sends the fullscreen command to MPLayer (doesnothing :( )
		"""
		info("trying to go fullscreen")
		self.send_command("vo_fullscreen 1")

	def _readlines(self):
		""" Reads the output of MPlayer in the pipe
		in stdin and stdout, and sends the result lines if any

		"""
		ret = []
		# print "readline"
		something_read = True

		while something_read :
			candidates_files = [self.process.stdout,
					self.process.stderr]
			watched_files = [self.process.stdout.fileno(), \
					 self.process.stderr.fileno()]

			(output_files, _, _) = select\
					.select(watched_files, [], [], 0.6)
			
			debug("something selected ??")
			something_read = False
			for output_file in output_files :
				#print("looks like it in desc:{0}".format(x))
				output_file = [ o_file for o_file 
						in candidates_files 
						if o_file.fileno() == output_file ]\
						[0] 
				ret.append(output_file.readline() )
				something_read = True
		return ret

	def seek(self, time):
		""" seeks the video stream to a second """
		command = "seek {0} 2".format(time)
		self.send_command(command)

	def get_subtitles_delay(self):
		""" Get the current delay of the subtitles 
		setted in MPlayer
		"""

		# get_property sub_delay
		res = self.send_command_with_result("get_property sub_delay")
		couple = re.match(r"ANS_sub_delay=(-?\d+\.\d+).*", res)

		return float(couple.group(1))

	def set_subtitles_delay(self, delay):
		""" Sets the subtitle delay, in seconds ?? """
		command = "sub_delay {0} 1".format(delay)
		self.send_command(command)
	
	def load_subtitle(self, filename):
		""" Loads a subtitle file""" 
		self.send_command("sub_remove")
		command = "sub_load \"{0}\"".format(filename)
		self.send_command_ignoring_results(command)
		self.send_command("sub_file 1")


def test():
	""" Useless for now """ 
	print("Put here the unit tests ...")
	# self.uifile = os.expanduser("~/share/MplayerTestUI.ui")
	# self.wTree = gtk.Builder()
	# self.wTree.add_from_file(self.uifile)
	# MPlayer = MPlayerSlave()

	# window = wTree.get_object("MainWindow")
	# if window:
    	# 	window.connect("destroy", gtk.main_quit)


	# dic = { "on_button1_clicked" : self.button1_clicked, 
    	# 	"on_MainWindow_destroy" : gtk.main_quit}
	# wTree.connect_signals(dic)

if __name__ == "__main__":
	test()
