#! /usr/bin/python


class torrent_finder:
	def __init__(self):
		pass
	def find_magnet_for(serie,num_season,num_ep):
		pass




# most simple API in the world for now : 
# is supposed to take a filename and do automatically all the work and downloading the subtitle in the same path.
	def get_for_ep(self,nom_serie,):
		pass

from lxml import etree
from StringIO import StringIO as StringIO

import httplib
import urllib
import zipfile
import os
import sys

class result(object):
	def __init__(self,html):
		self.html=html
		self.filename=None

#class result_factory(object):
	#@classmethod
	#request_filename="div[@class='detName']/a/"

class TPBMagnetFinder(torrent_finder):

	
	request_filename="div[@class='detName']/a"
	
	def __init__(self):
		self.server="thepiratebay.se"
		self.parser= etree.HTMLParser()

	def result_from_tablerow(self,row):
		res = result(row)
		filename_div = row.xpath(self.request_filename)
		print(filename_div)
		filename =filename_div[0].xpath("a")
		res.filename = filename_div[0].attrib["title"]
		return res

	def get_pattern(self,season,ep):
		return "S{0:02d}E{1:02d}".format(season,ep)

	def get_search_results(self, serie, season, ep):
		h1 = httplib.HTTPConnection(self.server)

		h1.set_debuglevel(10)
		url="/search/{0}%20{1}/0/7/0".format(serie,self.get_pattern(season,ep))
		print url
		h1.request("GET",url,headers={'User-Agent':"Mozilla/5.0 (X11; Linux i686; rv:10.0.4) Gecko/20100101 Firefox/10.0.4 Iceweasel/10.0.4"})

		print "trying to connect ..."
		r1 = h1.getresponse()
		print(r1)
		import pdb

		data = r1.read()
		print "data read"
		print(r1)
		return data

	def extract_table_result(self,request_html):
		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(request_html),parser)

		request = "//table[@id='searchResult']"
		table = (tree.xpath(request)[0])
	
		request = "//td[div[@class='detName']]"

		results = map(lambda x:self.result_from_tablerow(x),table.xpath(request))
		map(lambda x: sys.stdout.write(x.filename),results)
		return results

	def get_candidates(self,serie,season,ep):
		html= self.get_search_results(serie,season,ep)
		results =self.extract_table_result(html)
	
if __name__ == "__main__":
	obj = TPBMagnetFinder()

	obj.get_candidates("Dexter",6,12)


#	res = obj.find_magnet_for("Dexter",6,12)
#	print resi[0].file_name
#	res2 = obj.get_for_ep("Treme",1,1)
#	print res2[0].file_name
