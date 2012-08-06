""" messages utilities, to pass object throw network"""

import pickle


class MessageEncoder(object):
	""" message encoder : encode an object to pass it throw network
	currently implemented via pickle
	The encoding / decoding format should be codec dependant
	"""
	def encode(self, message):
		""" Encoding an object, returns a (string/message) """
		return pickle.dumps(message)

	def decode(self, message):
		""" decode a (string/message) 
		Decode a string, returns a message """
		return pickle.loads(message)

