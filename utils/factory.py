#! /usr/bin/python
#encoding:utf-8

""" Generic class for enclosing class construction 
into a class, maybe similar to providers
"""

class FactoryFactory(object):
	"""
	TODO: find a better solution
	"""

	def __init__(self, cls):
		self.cls = cls

	def get(self, * args, **kwargs):
		""" Constructs the object """
		return self.cls(*args, **kwargs)
