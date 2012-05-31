#! /usr/bin/python
#encoding:utf-8

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

import socket
import httplib
import urllib
import zipfile
import os
import sys

class result(object):
	def __init__(self,html):
		self.html=html
		self.filename=None
		self.magnet=None

#class result_factory(object):
	#@classmethod
	#request_filename="div[@class='detName']/a/"

class ConnectionException(Exception):
	def __init__(self,error,errno=None):
		Exception.__init__(self)
		self.errno=errno
		self.error=error


class TPBMagnetFinder(torrent_finder):
	request_filename="div[@class='detName']/a"
	request_magnet="a[starts-with(@href,'magnet')]"

	def __init__(self):
		self.server="thepiratebay.se"
		self.parser= etree.HTMLParser()

	def result_from_tablerow(self,row):
		"""
		constructs a function to extract informations (magnet and name)
		from HTML-tree row of TPB result table in search page. 
		"""

		res = result(row)
		filename_div = row.xpath(self.request_filename)

		# extraction of filename
		filename =filename_div[0].xpath("a")
		res.filename = filename_div[0].text #attrib["title"]

		# extraction of magnet link if present
		magnet_a = row.xpath(self.request_magnet)
		res.magnet = magnet_a[0].attrib["href"]

		return res

	def get_pattern(self,season,ep):
		""" returns filename patterns suech as "S01E12"
		"""
		return "S{0:02d}E{1:02d}".format(season,ep)

	def get_search_results(self, serie, season, ep):
		"""
		returns a string in which the HTML of the request is stored
		"""
		try:
			h1 = httplib.HTTPConnection(self.server)
			 #h1.set_debuglevel(10)
			url="/search/{0}%20{1}/0/7/0".format(serie,self.get_pattern(season,ep))
			h1.request("GET",url,headers={'User-Agent':"Mozilla/5.0 (X11; Linux i686; rv:10.0.4) Gecko/20100101 Firefox/10.0.4 Iceweasel/10.0.4"})
			r1 = h1.getresponse()
		except OSError as (errno,error):
			print "impossible de se connecter au serveur"
			raise ConnectionException(error)
		except socket.gaierror as er:
			raise ConnectionException(er)
		except socket.timeout as er:
			raise ConnectionException(er)
		except:
			raise ConnectionError(None)

		data = r1.read()
		return data

	def extract_table_result(self,request_html):
		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(request_html),parser)
		
		request = "//table[@id='searchResult']"
		table = (tree.xpath(request)[0])
	
		request = "//td[div[@class='detName']]"
		results = map(lambda x:self.result_from_tablerow(x),table.xpath(request))
		
		return results

	def get_candidates(self,serie,season,ep):
		html= self.get_search_results(serie,season,ep)
		results =self.extract_table_result(html)
		return results

		
	
if __name__ == "__main__":
	obj = TPBMagnetFinder()
	obj.get_candidates("Dexter",5,12)


