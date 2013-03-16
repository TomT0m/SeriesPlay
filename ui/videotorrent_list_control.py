#! /usr/bin/python
#encoding : utf-8
""" python file containing Video Finder logic """


from datasource.video_finder_client import \
	NetworkEpisodeVideoFinder as episode_video_finder

from ui.videotorrent_list_model import VideoResultStore

from utils.on_event_deferred import OnEventDeferred

from snakeguice.decorators import inject

import logging

from utils.factory import FactoryFactory



class VideoFinderController(object):
	""" Controler class """

	@inject(video_finder_creator = FactoryFactory)
	def __init__(self, video_finder_creator):
		self.video_finder_creator = video_finder_creator

	def add_video_finder(self, app, episode):
		""" Adding a new finder to the app"""
		logging.info("adding video finder for ep {0}...".format(episode))
		finder = self.video_finder_creator.get()

		window = app.getitem("VideoSearchResultWindow")
		candidates_view = app.getitem("TorrentList")

		dl_button = app.getitem("ChooseTorrent")
		cancel_button = app.getitem("CancelChooseTorrent")

		clo = {"wait_for_click" : None}

		def choose(plop):#pylint: disable=W0613
			""" Callback when the user has chosen
			Action : triggers the dl_request
			"""
			(model, itera) = candidates_view.get_selection().get_selected()
			choice = model.get_value(itera, 0)
			logging.debug("{} {}".format(choice.filename, choice.magnet))
			finder.on_chosen_launch_dl(choice)
			
			return choice	

		def chosen(dl_choice):
			""" callback to hide window"""
			window.hide()
			return dl_choice

		def on_cancel_pressed(self):
			""" Callback : not choosing Yet """
			clo["wait_for_click"].cancel()
			window.hide()


		def on_candidates_found(self):
			""" Callback when results are back presents them
			to the user """
			candidates = finder.candidates
			store = VideoResultStore(candidates)
			logging.debug("candidates ... {}".format(candidates_view))
			candidates_view.set_model(store.get_model())
			clo["wait_for_click"] = OnEventDeferred(dl_button, "clicked")
			clo["wait_for_click"].addCallback(choose).addCallback(chosen)

			cancel_button.connect("clicked", on_cancel_pressed)

			window.present()

		finder.connect("candidates_found", #pylint: disable = E1101
				on_candidates_found)

		finder.search_newep(episode)


