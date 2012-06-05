#!/usr/bin/python
#encoding:utf-8


from gi.repository import Gtk,GObject

class video_result_store(object):
	"""GTK store for video candidates results
	"""
	def __init__(self,candidates,model = None):
		self.candidates = candidates
		if not model:
			self.model=Gtk.ListStore(object,str)
		else:
			self.model = model

		for candidate in candidates:
			print "appending res to model"
			self.model.append([candidate,candidate.filename])

	def get_model(self):
		print "getting model"
		return self.model


def filename_text_getter(column,cell,model,itera,unknown = None):
	# print model
	# print 'getter called'
	# print column
	# import pdb ; pdb.set_trace()
	cell.set_property('text', model.get_value(itera, 0).filename)


def init_torrentlist_viewer(viewer):
	#cellpb = Gtk.CellRendererText()
	cellpbtext = Gtk.CellRendererText()
	filename=Gtk.TreeViewColumn("Name",cellpbtext)
	print "initting"
	filename.set_cell_data_func(cellpbtext,filename_text_getter)
	#self.iface.getitem("TorrentList").append_column(filename)
	viewer.append_column(filename)
	print "initted"

#class finder_viewer(GObject.GObject):
#	def __init__()

