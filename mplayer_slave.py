#encoding:utf-8
#! /usr/bin/python2.6


import cli
import subprocess

import os
import select
import re

 

class player:
	class PropertyUnknown(Exception):
		def __init__(self,msg):
			Exception.__init__(self,msg)	

	def __init__(self,vid=None):
		command=cli.command_line_generator("mplayer")
		command.add_option_single("-slave")
		command.add_option_single("-quiet")
		command.add_option_single("-idle")
		if vid != None:
			command.add_option_param("-wid",unicode(vid))
			
		self.process = subprocess.Popen(command.get_command(), shell=False, stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		self.process.poll()
		#print(self.process.poll())
	def launch(self,video_filepath,subfile_path=None):
		none

	def send_command(self,command):
		# self.process.stdin.flush()
		# print("sending command : \"{0}\"".format(command))
		# print ("lignes lues : ",self._readlines())
		self.process.stdin.write(command+ "\n")
		#self.process.stdin.flush()
		#result = self._readlines()[0]

	def send_command_with_result(self,command):
		self.send_command(command)
		result = []
		found = False
		while not found :
			result = self._readlines() 
			for x in result :
				# print ("analysing line '{0}'".format(x))
				# print  (x.find("ANS_"))
				if x.find("ANS_")==0:
					retour = x
					found=True
					break

				if x.find("-1")==0:
					retour=None
					found=True

		# print ("yeah !!",retour)
		return retour

	def send_command_ignoring_results(self,command):
		self.send_command(command)
		lines = self._readlines()
		#for x in lines :
			# print(x)

	def get_property(self,prop):
		# print("getting property", prop)
		
		result = self.send_command_with_result("get_property "+prop)
		#print("Mplayer result : '{0}'".format(result))
		if re.search("ANS_ERROR=PROPERTY_UNKNOWN", result):
			raise PropertyUnknown("Property unknown")

		if re.search("ANS_ERROR=PROPERTY_UNAVAILABLE",result):
			return False
		couple = re.match(r"ANS_"+prop+"=(\d+(\.\d+)?).*", result)
		# if couple:
		return couple.group(1)
		

	def get_current_seconds(self):
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

	def set_current_file(self,file):
		pass
	def end_player(self):
		self.process.kill()
	def play(self,filename) : 
		command="loadfile \"%s\"" % (filename)
		self.send_command(command)
	def get_video_resolution(self):
		print("getting video resolution")
		#res = self.send_command_with_result("get_video_resolution")
		width=self.get_property("width")
		height = self.get_property("height")
		#couple = re.match(r"ANS_VIDEO_RESOLUTION='(\d+) x (\d+)'.*", res)
		# print couple 
		return int(width),int(height)

	def set_fullscreen(self):
		print("trying to go fullscreen")
		self.send_command("vo_fullscreen 1")
        def _readlines(self):
		ret = []
		# print "readline"
		something_read=True
        	while something_read :
			fichiers_candidats= [self.process.stdout,self.process.stderr]
			(fic_descs,_,_)=select.select([self.process.stdout.fileno(),self.process.stderr.fileno()], [], [], 0.6)
			#print("something selected ??")
			something_read=False
            		for x in fic_descs :
				#print("looks like it in desc:{0}".format(x))
				x=[ fichier for fichier in fichiers_candidats if fichier.fileno()==x ][0] 
				ret.append(x.readline() )
				something_read=True
			# print ("currently reading",ret)
		# print "line read"
        	return ret
	def seek(self,time):
		command = "seek {0} 2".format(time)
		self.send_command(command)

	def get_subtitles_delay(self):
# get_property sub_delay
# ANS_sub_delay=0.000000
# ANS_ERROR=PROPERTY_UNAVAILABLE
		res = self.send_command_with_result("get_property sub_delay")
		couple = re.match(r"ANS_sub_delay=(-?\d+\.\d+).*", res)

		return float(couple.group(1))

	def set_subtitles_delay(self,delay):
		command = "sub_delay {0} 1".format(delay)
		self.send_command(command)
	
	def load_subtitle(self,filename):
		self.send_command("sub_remove")
		command = "sub_load \"{0}\"".format(filename)
		self.send_command_ignoring_results(command)
		self.send_command("sub_file 1")

#class TestUi:

if __name__ == "__main__":

	
        print("Put here the unit tests ...")
	# self.uifile = os.expanduser("~/share/MplayerTestUI.ui")
	# self.wTree = gtk.Builder()
	# self.wTree.add_from_file(self.uifile)
	MPlayer = player()

	self.window = self.wTree.get_object("MainWindow")
	if self.window:
    		self.window.connect("destroy", gtk.main_quit)


	dic = { "on_button1_clicked" : self.button1_clicked, 
    		"on_MainWindow_destroy" : gtk.main_quit}
	self.wTree.connect_signals(dic)

