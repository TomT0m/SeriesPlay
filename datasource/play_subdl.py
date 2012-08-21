#! /usr/bin/python
#encoding: utf-8
""" Module with subtitles : Search and downloads subtile class 
@class Subdownloader
"""

from logging import info, debug

def thr_sub_dl(model, subdl):
	"""
TODO : Passer à twisted ?
Téléchargment des sous-titres dans un thread
	"""
 
	info("thr method : calling")
	serie = model.get_current_serie()
	
	nom = serie.name
	path = serie.get_path_to_current_season()
	numep = serie.get_current_episode_number()
	numsais = serie.get_current_season_number()
	
	subdl.get_for_ep(serie.name, numsais, numep, path) 

class Subdownloader(object):
	""" Base class for a subdownloader
	Most simple API in the world"""
	def __init__(self):
		pass
	
	def get_for_ep(self, serie_name, season_number, 
			episode_number, destination_directory):
		""" @serie_name : string
		    @episode_number : number
		    @season_number : number
		    @destination directory : string
			
		is supposed to take a filename and do automatically all the work and downloading the subtitle in the same path.
			"""
		pass

class EmptySubdownloader(object):
	""" Dummy subdownloader, interface like class for subdownloader """
	def __init__(self):
		self.results = []
		debug("initialized")

	def get_founded_subtitles(self):
		""" results getter """
		return self.results


from lxml import etree
from StringIO import StringIO as StringIO

import httplib
import urllib
import zipfile
import os

class TVsubtitlesSubdownloader(Subdownloader):
	""" Subdownloader specialized and implemented 
	for tvsubtitles.org"""
	
	@classmethod
	def get_data_from_url(cls, url):
		""" downloads the html string from a url
		(should be refactored)
		"""
		stream = urllib.urlopen(url)
		data = stream.read()
		return data
	@classmethod
	def get_allserie_list(cls):
		""" Getting the website serie list page
		html string
		"""
		connection = httplib.HTTPConnection('www.tvsubtitles.net')
		connection.request("GET","/tvshows.html")
		stream = connection.getresponse()
		data = stream.read()
		return data

	#def dl_serie_allsub(self,filename):
	#	pass	

	@classmethod
	def get_serie_id(cls, nom_serie):
		""" get the website serie id from
		@nom_serie : the serie name string
		"""

		debug("------------------------------------------------------")
		data = cls.get_allserie_list()

		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(data), parser)

		# request = 
		# '/html/body/div/div[3]/div/table/tr/td/table/tr/td/table/tr[23]/td[2]/a/b'
		
		request = '/html/body'
		request = "//table[@id='table5']"

		table = (tree.xpath(request)[0])
		#print (table.tag)
		#print (table)
		#print (etree.tostring(table,pretty_print=True))

		escape_name = '{' + nom_serie+'}'
		escape_name = nom_serie
		req2 = "tr/td/a/b[contains(text(),'{0}')]".format(escape_name)
		req3 = "tr/td[contains(a/b/text(),'{0}')]/a".format(escape_name)
		debug("requests : {}, {} ".format(req2, req3))
		res = table.xpath(req2)
		debug(res)
		debug(etree.tostring(table.xpath(req2)[0]))
		elem_a = table.xpath(req3)[0]
		url = elem_a.attrib["href"]
		num = url.split("-")[1]
		info("extracting from {0} : {1}".format(url, num))
		return num

	@classmethod
	def get_episode_id(cls, num_saison, num_ep, html):
		""" searches the website id from an episode
		in a webpage string
		"""

		ep_string_ref = '{0}x{1:02d}'.format(num_saison, num_ep)

		# request = 
		# '/html/body/div/div[3]/div/table/tr/td/table/tbody/tr/td/table/tr[2]/td'
		
		request = "//table[@id='table5']"

		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(html), parser)
		
		table = (tree.xpath(request)[0])
		debug(etree.tostring(table, pretty_print=True))
		
		req_row_ep = "tr[contains(td/text(),'{0}')]"\
				.format(ep_string_ref)
		debug(req_row_ep)
		req_row_ep = "tr[td/text()='{0}']".format(ep_string_ref)
		debug(req_row_ep)
		ep_row = table.xpath(req_row_ep)
		debug (etree.tostring(ep_row[0], pretty_print=True))
		req_url = "td/a"
		link = ep_row[0].xpath(req_url)
		url = link[0].attrib["href"]

		ep_id = url.split("-")[1].split(".")[0]

		return ep_id

	@classmethod
	def get_sublist_from_epid_url(cls, ep_id, lang="en"):
		""" calculates the url associated to an episode id"""
		# http://www.tvsubtitles.net/episode-34678-en.html
		return "http://www.tvsubtitles.net/episode-{0}-{1}.html".format(ep_id, lang)
	@classmethod
	def get_season_dl_url(cls, num_serie, num_saison, lang="en"):
		""" calculates the url associated to a season"""
		return "http://www.tvsubtitles.net/download-{0}-{1}-{2}.html"\
				.format(num_serie, num_saison, lang)

	@classmethod
	def get_season_subtitles_html_url(cls, num_serie, num_saison):
		""" calculated the url associated to a season (all languages ??)"""
		return "http://www.tvsubtitles.net/tvshow-{0}-{1}.html"\
				.format(num_serie, num_saison)

	@classmethod
	def unzip_file(cls, filename, destination):
		""" unzip a zip file into destination rep"""
		archive = zipfile.ZipFile(filename,"r")
		archive.extractall(destination)
		info("fichier : {1} ; destination : {0}".format(destination, filename))

	def get_for_season(self, nom_serie, num_saison, rep_destination):
		""" downloads subtitles for an entire season to rep_destination directory"""
		info("------------------------------------------------------")
		# data = self.get_allserie_list()
		num = self.get_serie_id(nom_serie) 

		url_dl = self.get_season_dl_url(num, num_saison)
	
		info("Downloading to {}".format(url_dl))
		zip_filename = os.path.join(rep_destination, 
				"{0}-s{1}.zip".format(nom_serie, num_saison))
		urllib.urlretrieve(url_dl, zip_filename)
		
		self.unzip_file(zip_filename, rep_destination)

		info("------------------------------------------------------")

	@classmethod
	def get_all_files_id(cls, data_sublist):
		""" gets the subtitles files id from the 
		html page presenting the list of subtitles"""
		req = '/html/body/div/div[3]/div/a[div/@class="subtitlen"]'
		
		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(data_sublist), parser)
		a_elems = tree.xpath(req)
	
		return [a_elem.attrib['href'].split("-")[1].split(".")[0] 
				for a_elem in a_elems]
		#return map( lambda a_elem: 
		# a_elem.attrib['href'].split("-")[1].split(".")[0], a_elems)

	@classmethod
	def get_url_from_subid(cls, subid):
		""" calculates the url presenting a specified subtitle file"""
		return "http://www.tvsubtitles.net/download-{0}.html".format(subid)

	@classmethod
	def download_list(cls, epid_list, destination):
		""" Download and extracts the epid 
		list into destination """
		for epid in epid_list:
			url = cls.get_url_from_subid(epid)
			info("url {} :".format(url))
			data = cls.get_data_from_url(url)

			stream = StringIO(data)
			zipstream = zipfile.ZipFile(stream, 'r')
			
			zipstream.extractall(destination)

	def get_for_ep(self, nom_serie, num_saison, numep, rep_destination):
		""" Finds, downloads and copies to rep_destination subtitles for an episode
		"""
		info("------------------------------------------------------")
		num = self.get_serie_id(nom_serie) 

		url_dl = self.get_season_dl_url(num, num_saison)
	
		info("downloading from {}".format(url_dl))

		sub_list_url = self.get_season_subtitles_html_url(num, num_saison)
		sub_list_html = self.get_data_from_url(sub_list_url)

		id_ep = self.get_episode_id(num_saison, numep, sub_list_html)

		debug("Ep ID:{0}".format(id_ep))
		
		url_subs = self.get_sublist_from_epid_url(id_ep)
		debug(url_subs)
		sub_list_html = self.get_data_from_url(url_subs)

		liste = self.get_all_files_id(sub_list_html)

		debug("subtitles list :".format(liste))
		
		self.download_list(liste, rep_destination)
		info("------------------------------------------------------")


def main():
	""" testing function """

	obj = TVsubtitlesSubdownloader()
	
	obj.get_for_ep("Dexter", 6, 12, "./dst")
	obj.get_for_ep("Treme", 1, 1, "./dst")

if __name__ == "__main__":
	main()

