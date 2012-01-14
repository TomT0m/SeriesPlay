#! /usr/bin/python

import logging as logging

class NullHandler(logging.Handler):
    def emit(self, record):
	print(str(record))
	# print("logging",record)
        pass

h=NullHandler()

logging.getLogger("subdownloader.modules.metadata").addHandler(h)
logging.getLogger("subdownloader.SDService.SDService").addHandler(h)
import subdownloader.modules as modules
from subdownloader.modules.FileManagement.FileScan import ScanFolder as ScanFolder

# logging.getLogger("subdownloader.modules.metadata").addHandler(logger.NullHandler))

from  subdownloader.modules import SDService 

class subdownloader_subdownloader:
	def __init__(self):
		print("connecting to server ...")
		self.sdservice = SDService.SDService("osdb")
		print(self.sdservice.is_connected())
	def get_status(self,filepath):
		pass

# most simple API in the world for now


	def get_from_filepath(self,filepath):
		print("plop for",filepath)
		print("connecting ...")
		(files,subs)=ScanFolder(filepath,recursively = False)
		print(["{0} : {1} \n".format(fic.getFilePath(),fic.getHash()) for fic in files])
		
		while not self.sdservice.is_connected():
			#elf.sdservice.is_connected()
			print("connecting ...")
			self.__init__()
		# self.sdservice.CheckSubHash(files)
		subs_found=self.sdservice.SearchSubtitles(language="en",files=files)
		print(subs)
		print(subs_found)

		# self.sdservice.connect()
		pass

if __name__ == "__main__":
	import sys
	logging.basicConfig()
	print "Testing !!"
	print "... connecting ..."
	logging.getLogger("subdownloa").addHandler(h)

	dl = subdownloader_subdownloader()
	for arg in sys.argv[1:] :
		print("dl for folder {0}".format(arg))
		dl.get_from_filepath(arg)

	print "... done ..."

