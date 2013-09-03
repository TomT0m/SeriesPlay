
#encoding:utf-8
"""
Managing series states : not display a Serie if it has no newep for example.


"""
from gi.repository import GObject.GObject as Gobj


class SeriesController(Gobj):
	"""
	Serie Combo management
	Initialises and manage what is displayed in the main SerieCombo.

	OnlyNewEpMode:
		Displaying Series in combo choices if and only if there is unseen eps for the Serie.
	AllEpMode:
		Displays everything
	* Recieving new ep envents 
	"""
	def __init__(self, combo, model):
		""" @combo: the GtkCombobox displaying the serie list to users """

		self.serie_combo = combo
		self.series = model

		for serie in model:
			s_obj = SerieController(serie, self)
			s_obj.connect()



class SerieController(Gobj):
	""" 
	"""
	def __init__(self, serie_obj, series_controller):
		self.serie_obj = serie_obj
		self.series_controller = series_controller
		self.state = 

	def 

