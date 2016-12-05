'''
@original author: Maciej Wasilak
@music player additions by: Ethan Fetsko and Cory Lehnert
'''

import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap


import pygame
import time
from random import randint
##IOT addition

pygame.init()
pygame.mixer.init()
nextSong = ""
UNQueue = ""
songSep = 0
listOfSongs = ["Second Chance.wav", "3.mp3", "4.mp3", "5.mp3"]
###

class PlayResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify()

    def notify(self):
        log.msg('PlayResource: ')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        global UNQueue
        print 'PUT payload: ' + request.payload
       
        if(UNQueue == ""):
            currentSong = listOfSongs[randint(0,3)]
        else:
            songSep = UNQueue.find(",")
            currentSong = UNQueue[0:songSep]
            UNQueue = UNQueue[(songSep + 1):]
        pygame.mixer.music.load(currentSong)
        pygame.mixer.music.play(1, 0.0)
        payload = ("Now playing: " + currentSong)
        response = coap.Message(code=coap.CHANGED, payload=payload)
        return defer.succeed(response)
    
class PauseResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify()

    def notify(self):
        log.msg('PauseResource: ')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        print 'PUT payload: ' + request.payload
        payload = "Music paused."
        response = coap.Message(code=coap.CHANGED, payload=payload)
        pygame.mixer.music.pause()
        return defer.succeed(response)

class UpNextResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify

    def notify(self):
        log.msg('UpNextResource: ')
        self.updateState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        global UNQueue
        print 'PUT payload: ' + request.payload
        payload = 'Next song: ' + request.payload
        nextSong = request.payload
        for song in listOfSongs:
            if(nextSong == song):
                UNQueue = UNQueue + (nextSong + ",")
                response = coap.Message(code=coap.CHANGED, payload=payload)
            else:
                response = coap.Message(code=coap.CHANGED, payload="There is no song containing this name")
        
        
        return defer.succeed(response)
    
    def render_GET(self, request):
        print "GET payload:  " + UNQueue
        response = coap.Message(code=coap.CONTENT, payload=UNQueue)
        return defer.succeed(response)
        

# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()


###IOT addition
pause = PauseResource()
root.putChild('pause', pause)

play = PlayResource()
root.putChild('play', play)

upNext = UpNextResource()
root.putChild('next', upNext)
###

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
