#! /usr/bin/pytohn
#encoding:utf-8


import gobject
from twisted.internet import gtk2reactor,threads,defer

import dl_manager
import play_tpb_search

class episode_finder(gobject.GObject):
        __gsignals__={ 
                'candidates_found' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()), 
                'file_downloaded' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()), 
                'download_launched' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())  
        }
	def __init__(self,episode):
		gobject.GObject.__init__(self)
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

