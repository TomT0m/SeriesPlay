#! /usr/bin/python
#encoding:utf-8
"""
A ThePirateBay magnet source
"""


from lxml import etree
from StringIO import StringIO as StringIO

from logging import debug, info

import socket
import httplib
import re

class Result(object):
	""" base class for found magnet storage """
	def __init__(self, html):
		# self.html = html
		self.filename = None
		self.magnet = None
		self.leechers = None
		self.filesize = None

class TorrentFinder(object):
	""" base class for magnet and torrent finder
	"""
	def __init__(self):
		pass
	def find_magnet_for(self, serie, num_season, num_ep):
		""" prototype for the search method
		@returns a set of Result
		"""
		pass
# most simple API in the world for now : 
	def get_for_ep(self, serie, num_ep):
		""" Obsolete ?
		is supposed to take a filename and do automatically all the work and downloading the subtitle in the same path.
		"""
		pass


#class result_factory(object):
	#@classmethod
	#request_filename="div[@class='detName']/a/"

class ConnectionException(Exception):
	""" Exception for network connection problems, in general
	"""
	def __init__(self, error, errno=None):
		Exception.__init__(self)
		self.errno = errno
		self.error = error


class TPBMagnetFinder(TorrentFinder):
	"""
	Magnet finder implemented for The Pirate Bay
	"""
	request_filename = "div[@class='detName']/a"
	request_magnet = "a[starts-with(@href,'magnet')]"

	def __init__(self):
		TorrentFinder.__init__(self)
		self.server = "thepiratebay.sx"
		self.parser = etree.HTMLParser()

	def result_from_tablerow(self, row):
		""" constructs a Result from a HTML row element of TPB
		"""
		torrent_td_request = "td[div[@class='detName']]"
		torrent_td = row.xpath(torrent_td_request)[0]
		
		result = self.result_from_torrent_td(torrent_td)
		
		# leechers extraction
		leechers_div = row.xpath("td[@align='right']")[0]
		result.leechers = int(leechers_div.text)

		return result

	def extract_filesize(self, td_elem):
		""" not implemented"""
		pass

	def result_from_torrent_td(self, td_elem):
		"""
		constructs a function to extract informations (magnet and name)
		from HTML-tree row of TPB result table in search page. 
		"""

		res = Result(td_elem)
		filename_div = td_elem.xpath(self.request_filename)

		# extraction of filename
		res.filename = filename_div[0].text #attrib["title"]

		# extraction of magnet link if present
		magnet_a = td_elem.xpath(self.request_magnet)
		res.magnet = magnet_a[0].attrib["href"]
		
		#extraction of file size
		magnet_info = td_elem.xpath("font[@class='detDesc']")[0].text
		filesize = re.search("Size(.*iB)", magnet_info)
	
		res.filesize = filesize.group(1)
	
		return res
	@classmethod
	def get_pattern(cls, season, episode):
		""" returns filename patterns suech as "S01E12"
		"""
		return "S{0:02d}E{1:02d}".format(season, episode)

	def get_search_results(self, serie, season, episode):
		"""
		returns a string in which the HTML of the request is stored
		"""
		response = None
		try:
			connection = httplib.HTTPConnection(self.server)
			#h1.set_debuglevel(10)
			serie = serie.replace(' ', '%20')
			url = "/search/{0}%20{1}/0/7/0"\
					.format(serie, self.get_pattern(season, episode))

			user_agent = \
"Mozilla/5.0 (X11; Linux i686; rv:10.0.4)\
 Gecko/20100101 Firefox/10.0.4 Iceweasel/10.0.4"
			heads = {
					'User-Agent' : user_agent
					}
			connection.request("GET", url, headers = heads) 
			debug("url request : {}, headers : >{}<".format(url, heads))

			response = connection.getresponse()

		except OSError as (errno, error): #pylint: disable=W0623
			info("impossible de se connecter au serveur  - errno {}, error {}"\
					.format(errno, error))
			raise ConnectionException(error)
		except socket.gaierror as err:
			raise ConnectionException(err)
		except socket.timeout as err:
			raise ConnectionException(err)
		except:
			raise ConnectionException(None)

		data = response.read()
		debug('results <<<<{}>>>>'.format(data))
		return data

	def extract_table_result(self, request_html):
		""" Calculates a set of Result 
		from a html TPB result page string"""
		parser = etree.HTMLParser()
		debug('html : >>>>>{}<<<<< '.format(request_html))
		tree = etree.parse(StringIO(request_html), parser)
		
		request = "//table[@id='searchResult']"
		table = (tree.xpath(request)[0])
	
		request = "//tr[td[div[@class='detName']]]"
		results = [self.result_from_tablerow(x) for x in table.xpath(request)] 
		# results = map(lambda x:self.result_from_tablerow(x), table.xpath(request))
		
		return results

	def get_candidates(self, serie, season, episode):
		""" Get candidates Results by performing a request on TPB
		"""
		html = self.get_search_results(serie, season, episode)
		results = self.extract_table_result(html)
		return results

		
def test():
	""" Main test function (obsolete) """
	obj = TPBMagnetFinder()
	obj.get_candidates("Dexter", 5, 12)


if __name__ == "__main__":
	test()
