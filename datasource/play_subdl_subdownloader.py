#! /usr/bin/python
#encoding : utf-8
""" unused file ???
Untested stub for "subdownloader" for opensubtitles website
"""

import logging as logging

class NullHandler(logging.Handler):
	""" Dummy log handler, justs prints"""
	def emit(self, record):
		print(str(record))

LOG_HANDLER = NullHandler()

logging.getLogger("subdownloader.modules.metadata").addHandler(LOG_HANDLER)
logging.getLogger("subdownloader.SDService.SDService").addHandler(LOG_HANDLER)

#import subdownloader.modules as modules

from subdownloader.modules.FileManagement.FileScan \
		import ScanFolder as ScanFolder

from  subdownloader.modules import SDService 

class SubdownloaderSubdownloader:
	""" Subdownloader for 'subdownloader' API """
	def __init__(self):
		print("connecting to server ...")
		self.sdservice = SDService.SDService("osdb")
		print(self.sdservice.is_connected())
	def get_status(self, filepath):
		""" ??? """ 
		pass

# most simple API in the world for now

	def get_from_filepath(self, filepath):
		""" gets a subtitle for a file """
		print("plop for", filepath)
		print("connecting ...")
		(files, subs) = ScanFolder(filepath, recursively = False)
		print(["{0} : {1} \n".format(fic.getFilePath(), fic.getHash()) for fic in files])
		
		while not self.sdservice.is_connected():
			#elf.sdservice.is_connected()
			print("connecting ...")
			self.__init__()
		# self.sdservice.CheckSubHash(files)
		subs_found = self.sdservice.SearchSubtitles(language="en", files=files)
		print(subs)
		print(subs_found)

		# self.sdservice.connect()

def test():
	import sys
	logging.basicConfig()
	print "Testing !!"
	print "... connecting ..."
	logging.getLogger("subdownloa").addHandler(LOG_HANDLER)

	downloader = SubdownloaderSubdownloader()
	for arg in sys.argv[1:] :
		print("dl for folder {0}".format(arg))
		downloader.get_from_filepath(arg)

	print "... done ..."

if __name__ == "__main__":
	test()
