#!/usr/bin/python 
#encoding:utf-8
""" Main script for launching a episode finder server
(different process for avoiding compatibility of twisted version, 
temporary workaround and toying with twisted for trying it)
"""

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


from datasource.episode_video_finder import EpisodeFinderServerFactory


def main():
	""" Launches the server """
	logging.basicConfig(level=logging.DEBUG, filename='plop.log')
	logging.warning("plop")
	print("plop")
	endpoint = TCP4ServerEndpoint(reactor, 8010)
	endpoint.listen(EpisodeFinderServerFactory())
	reactor.run() # pylint: disable=E1101

if __name__ == "__main__":
	main()

