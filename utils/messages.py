import pickle


class message_encoder(object):
	def encode (self,message):
		return pickle.dumps(message)
	def decode(self,message):
		return pickle.loads(message)

