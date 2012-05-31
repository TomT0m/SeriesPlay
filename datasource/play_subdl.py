#! /usr/bin/python




class subdownloader:
	def __init__(self):
		pass
	def get_status(self):
		pass
	
# most simple API in the world for now : 
# is supposed to take a filename and do automatically all the work and downloading the subtitle in the same path.
	def get_for_ep(self,nom_serie,):
		pass

class EmptySubdownloader():
	def __init__():
		print("initialized")

	def get_status_string():
		return "Always here for you !"

	def get_founded_subtitles():
		return results


from lxml import etree
from StringIO import StringIO as StringIO

import httplib
import urllib
import zipfile
import os

class TVsubtitlesSubdownloader(subdownloader):

	def get_data_from_url(self,url):
		f=urllib.urlopen(url)
		data = f.read()
		return data

	def get_allserie_list(self):
		
		h1 = httplib.HTTPConnection('www.tvsubtitles.net')
		h1.request("GET","/tvshows.html")
		r1 =h1.getresponse()
		data = r1.read()
		return data

	#def dl_serie_allsub(self,filename):
	#	pass	

	def get_serie_id(self, nom_serie):
		print("------------------------------------------------------")
		data = self.get_allserie_list()

		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(data),parser)

		request = '/html/body/div/div[3]/div/table/tr/td/table/tr/td/table/tr[23]/td[2]/a/b'
		
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
		print(req2,req3)
		res = table.xpath(req2)
		print res
		print (etree.tostring(table.xpath(req2)[0]))
		print "tadaaa !"
		elem_a=table.xpath(req3)[0]
		url = elem_a.attrib["href"]
		num = url.split("-")[1]
		print("extracting from {0} : {1}".format(url,num))
		return num

	def get_episode_id(self, num_saison, num_ep,html):

		ep_string_ref='{0}x{1:02d}'.format(num_saison,num_ep)

		request = '/html/body/div/div[3]/div/table/tr/td/table/tbody/tr/td/table/tr[2]/td'
		
		request = "//table[@id='table5']"

		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(html),parser)
		
		table=(tree.xpath(request)[0])
		print (etree.tostring(table,pretty_print=True))
		
		req_row_ep="tr[contains(td/text(),'{0}')]".format(ep_string_ref)
		print(req_row_ep)
		req_row_ep="tr[td/text()='{0}']".format(ep_string_ref)
		print(req_row_ep)
		# print(table.to_string())
		ep_row=table.xpath(req_row_ep)
		print (etree.tostring(ep_row[0],pretty_print=True))
		req_url = "td/a"
		link=ep_row[0].xpath(req_url)
		url=link[0].attrib["href"]

		ep_id=url.split("-")[1].split(".")[0]

		return ep_id
	def get_sublist_from_epid_url(self,ep_id,lang="en"):
		# http://www.tvsubtitles.net/episode-34678-en.html
		return "http://www.tvsubtitles.net/episode-{0}-{1}.html".format(ep_id,lang)

	def get_season_dl_url(self,num_serie,num_saison,lang="en"):
		return "http://www.tvsubtitles.net/download-{0}-{1}-{2}.html".format(num_serie,num_saison,lang)

	def get_season_subtitles_html_url(self,num_serie,num_saison):
		return "http://www.tvsubtitles.net/tvshow-{0}-{1}.html".format(num_serie,num_saison)

	def unzip_file(self,filename,destination):
		archive=zipfile.ZipFile(filename,"r")
		archive.extractall(destination)
		print("fichier : {1} ; destination : {0}".format(destination,filename))

	def get_for_season(self, nom_serie, num_saison, rep_destination):
		print("------------------------------------------------------")
		data = self.get_allserie_list()
		num = self.get_serie_id(nom_serie) 

		url_dl = self.get_season_dl_url(num,num_saison)
	
		print(url_dl)
		zip_filename= os.path.join(rep_destination,"{0}-s{1}.zip".format(nom_serie,num_saison))
		urllib.urlretrieve(url_dl,zip_filename)
		
		self.unzip_file(zip_filename,rep_destination)

		print("------------------------------------------------------")

	def get_all_files_id(self,data_sublist):
		req = '/html/body/div/div[3]/div/a[div/@class="subtitlen"]'
		
		parser = etree.HTMLParser()
		tree = etree.parse(StringIO(data_sublist),parser)
		a_elems = tree.xpath(req)
	
		return map( lambda a_elem: a_elem.attrib['href'].split("-")[1].split(".")[0] ,a_elems)

	def get_url_from_subid(self,subid):
		return "http://www.tvsubtitles.net/download-{0}.html".format(subid)

	def get_for_ep(self, nom_serie, num_saison, numep, rep_destination):
		
		print("------------------------------------------------------")
		data = self.get_allserie_list()
		num = self.get_serie_id(nom_serie) 

		url_dl = self.get_season_dl_url(num,num_saison)
	
		print(url_dl)
		#zip_filename= os.path.join(rep_destination,"{0}-s{1}.zip".format(nom_serie,num_saison))

		sub_list_url = self.get_season_subtitles_html_url(num, num_saison)
		sub_list_html=self.get_data_from_url(sub_list_url)

		id_ep=self.get_episode_id(num_saison,numep,sub_list_html)


		print("Ep ID:{0}".format(id_ep))

		#urllib.urlretrieve(url_dl,zip_filename)
		
		url_subs=self.get_sublist_from_epid_url(id_ep)
		print(url_subs)
		sub_list_html=self.get_data_from_url(url_subs)

		liste=self.get_all_files_id(sub_list_html)

		print(liste)
		
		for epid in liste:
			url=self.get_url_from_subid(epid)
			print(url)
			data=self.get_data_from_url(url)

			f=StringIO(data)
			zipstream=zipfile.ZipFile(f,'r')
			
			zipstream.extractall(rep_destination)

			# self.unzip_filself.get_url_from_subid(subid)
		#self.unzip_file(zip_filename,rep_destination)

		print("------------------------------------------------------")

	
if __name__ == "__main__":
	obj = TVsubtitlesSubdownloader()
	
	obj.get_for_ep("Dexter",6,12,"./dst")
	obj.get_for_ep("Treme",1,1,"./dst")
