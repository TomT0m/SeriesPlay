
#encoding:utf-8
"""
Managing series states : not display a Serie if it has no newep for example.

"""

from gi.repository.GObject import GObject as GObj
from gi.repository import GObject 

import logging

# from gi.repository import Gtk as Gtk

class SeriesController(GObj):
	"""
	Serie Combo management
	Initialises and manage what is displayed in the main SerieCombo.

	OnlyNewEpMode:
		Displaying Series in combo choices if and only if there is unseen eps for the Serie.
	AllEpMode:
		Displays everything
	* Recieving new ep envents 
	"""
	# __gtype_name__ = 'GtkSeries'

	def __init__(self, combo, model, injector):
		""" @combo: the GtkCombobox displaying the serie list to users """
		super(SeriesController, self).__init__()

		self.serie_combo = combo
		self.series = model
		self.injector = injector
		self.subcontrollers = []
		for iserie in model.series.items():
			serie = iserie[1]
			print(iserie)
			s_obj = SerieModel(serie, self)
			s_obj.connect("has_newep", self.when_serie_hasnewep)
			
			s_control = SerieController(s_obj, self)
			s_control.search_newep()

			self.subcontrollers.append(s_control)

	def init_view(self):
		""" initialisation of the view
		"""
		pass

	def when_serie_hasnewep(self, serie):
		"""
		callback when a serie has a new episode 
		"""
		print("found newep for serie {}".format(serie))


class SerieController(GObj):
	"""
		The newep and oldep manager
	"""
	
	__gsignals__ = {
		'has_newep' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
	}
	
	def __init__(self, serie_obj, series_controller):
		GObj.__init__(self)
		self.serie_obj = serie_obj
		print(serie_obj)
		self.series_controller = series_controller
		self.state = None


	def search_newep(self):
		"""
		Launches the async search of a new available ep for this serie.
		"""
		print(self.serie_obj)
		if self.serie_obj.season.episode.is_ready_to_watch():
			self.emit('has_newep', self)


class SerieModel(GObj):
	""" Model wrapper """
	__gsignals__ = {
		'has_newep' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
	}
	
	def __init__(self, sobj, controller):
		super(SerieModel, self).__init__()
		self.serie_obj = sobj
		self.controllar = controller

	def __str__(self):
		return '{} {} {}'.format(self.serie_obj.name, self.serie_obj.season.number, self.serie_obj.episode.number)



class SeriesView(GObj):
	"""
	The view for selectable series
	
	"""
	
	__gsignals__ = {
		'serie_selected' : (GObject.SIGNAL_RUN_LAST, SerieController, [SerieController]),
	}

	def __init__(self, combo):
		self.combo = combo

	def add_serie(self, serie):
		""" Adds a serie object to the selectable one
		"""
		self.combo.additem(serie) 

