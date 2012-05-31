#!/usr/bin/python -u
#encoding:utf-8

from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


from datasource.episode_video_finder import EpisodeFinderServer,EpisodeFinderServerFactory


endpoint = TCP4ServerEndpoint(reactor,8010)
endpoint.listen(EpisodeFinderServerFactory())
reactor.run()

