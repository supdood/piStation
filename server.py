'''
@original author: Maciej Wasilak
@temperature additions by: Ethan Fetsko and Cory Lehnert
'''

import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap

##
import pygame
import time

##IOT addition

pygame.init()
pygame.mixer.init()

if pygame.mixer:
    pygame.mixer.music.load('Second Chance.wav')

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
        print 'PUT payload: ' + request.payload
        payload = "Now playing music."
        response = coap.Message(code=coap.CHANGED, payload=payload)
        pygame.mixer.music.play(1, 0.0)
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

# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()


###IOT addition
pause = PauseResource()
root.putChild('pause', pause)

play = PlayResource()
root.putChild('play', play)
###

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
