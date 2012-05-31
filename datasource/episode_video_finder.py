#! /usr/bin/pytohn
#encoding:utf-8


from gi.repository import GObject
from twisted.internet import gtk2reactor,threads,defer

import dl_manager
import play_tpb_search
import test_dl_manager

class episode_finder(GObject.GObject):
        __gsignals__={ 
                'candidates_found' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
                'file_downloaded' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()), 
                'download_not_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),  
                'download_launched' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())  
        }
	def __init__(self,episode):
		GObject.GObject.__init__(self)
		self.episode = episode

	def search_newep(self,ep):
		def on_found(results):
			print "emitting candidates found"
			self.emit("candidates_found")
			return results

		finder = play_tpb_search.TPBMagnetFinder()
		d = threads.deferToThread(finder.get_candidates, ep.serie.nom,ep.num_saison,ep.num_ep )
		print "adding callbacks for searching new eps"		
		d.addCallback(self._got_candidates)
		d.addCallback(on_found)
		return d
	
	def _got_candidates(self,results):
		self.candidates = results
		return results

	def on_addition_success(self,result=None):
		print "emitting download_launched" 
		self.emit("download_launched")

	def on_addition_fail(self,error):
		print "emitting addition_fail"
		print(error.exception_msg)
		self.emit("download_not_launched")
		return error

	def on_chosen_launch_dl(self,chosen):
		adder = dl_manager.deluge_dl_adder(host="localhost") 

		print "download link ?"	
		dl_path = self.episode.serie.get_path_to_season(self.episode.num_saison)
		print "dl_path : {}".format(dl_path)
		print "____________"

		return adder.add_magnet(chosen.magnet,dl_path).addBoth(self.on_addition_success).addBoth(adder.cleanup)

