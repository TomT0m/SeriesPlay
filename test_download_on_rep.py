#! /usr/bin/python
#encoding: utf-8

from twisted.trial import unittest
from twisted.internet import defer,gtk2reactor as reactor
import gobject

from twisted.python.failure import Failure
from unittest import expectedFailure
# reactor.install()

import serie_manager
from episode_finder import episode_finder

import deluge.component as component
from deluge.log import setupLogger
setupLogger()

import sys,os

class OnEventDeferred(defer.Deferred,gobject.GObject):
	def __init__(self,obj,event,*args):
		defer.Deferred.__init__(self)
		gobject.GObject.__init__(self)
		obj.connect(event,self.emited,*args)

	def emited(self,*args):
		print "OnEventDeferred : event catched"
		self.callback(*args)

	def err_emited(self,*args):
		print "OnEventDeferred : err event catched"
		self.errback(*args)

	def add_error_event(self,obj,event,*args):
		obj.connect(event,self.err_emited,*args)	


class gobj(gobject.GObject):
	__gsignals__={
		'ok' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
		'error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,())
	}
	def __init__(self):
		gobject.GObject.__init__(self)


class testOnEventDeferred(unittest.TestCase):
	def testOK(self):
		obj = gobj()
		defe = OnEventDeferred(obj,"ok")
		obj.emit("ok")
		return defe # .maybeDeferred(defe)
		
#	@expectedFailure
	def testError(self): 
		obj = gobj()
		defe = OnEventDeferred(obj,"ok")
		defe.add_error_event(obj,"error")
		obj.emit("error")
		return defe.addCallbacks(self.fail, self.assertIsInstance, errbackArgs=(Failure,))

class DummySeriesManager(serie_manager.seriesManager):

	config_file_season_name=".play_conf"	
	config_file_serie_name=".play_season"
	config_file_abs_name="~/.play_season"

	path_to_series_var="BASE"
	play_current_episode_var="CUR"
	skip_time_var="GENERICTIME"
	decay_time_var="DECALAGESUB"
	serie_name_var="NAME"
	fps_var="SUBFPS"

	def __init__(self):
		self.executer=None #command_executer()

# paths generator
	def get_global_config_file(self):
		return os.path.expanduser(self.config_file_abs_name)

	def get_absolute_path(self):
		return os.path.join(os.getcwd(),"_tmp")

	def get_path_to_serie(self,nom):
		return os.path.join(os.getcwd(),"_tmp",nom)

	def get_path_to_current_season(self):
		return os.path.join(self.get_path_to_serie(),"saison6")

	def get_path_to_current_season_of_serie(self,name):
		return os.path.join(self.get_absolute_path(),"Dexter","saison6")
	
	def get_path_to_season(self,nom,numsaison):
		return os.path.join(self.get_absolute_path(),"Dexter","saison6")

	
# config management 
	def read_conf_var(self,config_file_path,var_name):
		return config_manager.read_conf_var(config_file_path,var_name)
	
	def write_conf_var(self,config_file_path,var_name,value):
		return config_manager.write_conf_var(config_file_path,var_name,value)
		
	def read_num_conf_var(self,config_file_path,var_name):
		return config_manager.read_num_conf_var(config_file_path,var_name)

	def get_conf_variable(self,nom,numsaison,var_name):
		return self.read_conf_var(self.get_path_to_season(nom,numsaison),var_name)

	def get_num_conf_variable(self,nom,numsaison,var_name):
		return self.read_num_conf_var(self.get_path_to_season(nom,numsaison),var_name)


# useful data getters
	def get_current_serie(self):
		return "Dexter"

	def get_num_current_saison(self,nom):
		return 6

	# @trace
	def get_serie_list(self):
		print("getting serie list")
		liste_en_chaine=command_executer().get_list_output(["series","-l"])

		print("got serie list")
		return liste_en_chaine

	def get_current_episode(self,nom_serie,num_saison):
		return 6

	def get_subtitle_candidates(self,nom_serie,num_saison,num_ep):
		return self.get_candidates(nom_serie,num_saison,num_ep,"-L")
	
	def get_video_candidates(self,nom_serie,num_saison,num_ep):
		return self.get_candidates(nom_serie,num_saison,num_ep,"-V")

	def get_candidates(self,nom_serie,num_saison,num_ep,option):
                path=self.get_path_to_season(nom_serie,num_saison)
                if os.path.exists(path):
                        command_g=command_line_generator("play")
                        command_g.add_option_param("-e",unicode(num_ep))
                        command_g.add_option_single(unicode(option))
                        return self.executer.get_list_output(command_g.get_command(),cwd=path)
                else:
                        return []




class testDownloadOnRep(unittest.TestCase):
	__gsignals__={
		'candidates_found' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'file_downloaded' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'download_launched' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}
			
	def setUp(self):
		""" 
		TODO : Creating a fake environment
		"""
		self.serie_manager = DummySeriesManager()
		
		self.serie = serie_manager.bashManagedSerie("Dexter",self.serie_manager)
		self.episode = serie_manager.bashManagedEpisode(self.serie,5,1)
		d = component.start()
		defer.gatherResults([d])
		try:
			os.makedirs(os.path.join(self.serie.get_path_to_serie(),'saison6'))
		except Exception:
			pass 
		return 

	def test_search(self):
		def print_results(results):
			print("Résultats {}".format(len(results)))
			return results
		ep_finder = episode_finder(self.episode)
		return ep_finder.search_newep(self.episode).addCallback(print_results)


	def test_search_for_ep(self):
		def print_results(results):
			print("Résultats {}".format(len(results)))
		ep_finder = episode_finder(self.episode)
		ep_find = ep_finder.search_newep(self.episode).addCallback(print_results)
		test = OnEventDeferred(ep_finder,"candidates_found")
		#defe = ep_find.search_newep(self.episode)
		return test.addCallback(self.assertTrue)

	def test_search_and_choose(self):
		ep_finder = episode_finder(self.episode)
		def print_results(results):
			print("Résultats {}".format(len(results)))
		def catch_err(res):
			print "err catched {}".format(res)
		def choose(res):
			print ep_finder.candidates[0]
			ep_finder.on_chosen_launch_dl(ep_finder.candidates[0])
			print "dl_launched ?" 
			return True

		final_test = OnEventDeferred(ep_finder,"download_launched")
		final_test.add_error_event(ep_finder,"download_not_launched")

		candidates_found = OnEventDeferred(ep_finder,"candidates_found").addCallback(choose).addErrback(catch_err)
		ep_find = ep_finder.search_newep(self.episode).addCallback(print_results)
		
		return final_test.addBoth(catch_err) # .addCallback(plop)#candidates_found.addCallback(final_test)# first_step.addCallback(final_test)
