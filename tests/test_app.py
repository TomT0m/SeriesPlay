#!/usr/bin/python
#encoding: utf-8
""" Module testing Torrent List Controller """

from twisted.trial import unittest
import twisted 




from tests.common_test import value, create_fake_env, create_app, print_app_status
from app.controller import get_combo_value



import app.service


#pylint:disable=R0904
class TestVideotorrentController(unittest.TestCase):
	""" Controller testcase :
	* create app
	* empty selection
	* selection
	* cancelation
		"""
	#pylint: disable=C0103 
	def setUp(self): 
		""" setting up """
		twisted.internet.base.DelayedCall.debug = True
		print("setting up")

		create_fake_env('ZPlop', 2, 2)
		create_fake_env('Plop', 3, 2)
	
	def test_1(self):
		""" Fake app creation """
		tapp = create_app()
		print_app_status(tapp)

		combo_box = tapp.getitem("SerieListCombo")
		combo_box.set_active(0)
		print_app_status(tapp)
		self.assertTrue(value(combo_box) == 'Plop')

		season = tapp.selected_season()
		self.assertEquals(season, 3)
		ep = tapp.selected_numep()
		
		self.assertEquals(ep, 2)

		combo_box.set_active(2)
		print_app_status(tapp)
		
		self.assertEquals(value(combo_box), 'ZPlop')
		
		self.assertEquals((tapp.selected_season(), tapp.selected_numep()), (2, 2))

		tapp.stop()

		return 

	def test_change_serie(self):
		""" TestCase : change serie on ui """
		tapp = create_app()
		control = tapp.event_mgr

		print_app_status(tapp)
		
		control.update_serie_view()

		print_app_status(tapp)
		# combo_box = app.getitem("SerieListCombo")
		print_app_status(tapp)

		numep_widget = tapp.getitem("numEpSpin")

		numep_widget.set_value(3)
		
		self.assertEquals(tapp.selected_numep(), 3)	
		print_app_status(tapp)


		numsais_widget = tapp.getitem("numSaisonSpin")

		numsais_widget.set_value(8)
		print_app_status(tapp)

		self.assertEquals((tapp.selected_season(), tapp.selected_numep()), (8, 1))

		plop = get_combo_value(tapp.getitem("CandidateSubsCombo"))
		self.assertEquals(plop, None)

		tapp.stop()
