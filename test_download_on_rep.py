#! /usr/bin/python
#encoding: utf-8

from twisted.trial import unittest
from twisted.internet import defer,gtk2reactor as reactor
import gobject

# reactor.install()

import serie_manager
from episode_finder import episode_finder




class OnEventDeferred(defer.Deferred,gobject.GObject):
	def __init__(self,obj,event,*args):
		defer.Deferred.__init__(self)
		gobject.GObject.__init__(self)
		obj.connect(event,self.emited,*args)

	def emited(self,*args):
		self.callback(*args)

#def assertEmited()
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
		return "_tmp"

	def get_path_to_serie(self,nom):
		return os.path.join("_tmp","nom")

	def get_path_to_current_season(self):
		return os.path.join(self.get_path_to_serie(),"saison6")

	def get_path_to_current_season_of_serie(self,name):
		return "_tmp/Dexter/saison6"
	
	def get_path_to_season(self,nom,numsaison):
		return "_tmp/Dexter/saison6"

	
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
		pass

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

