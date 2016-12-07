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
import threading, time
import sys

## music player
pygame.init()
pygame.mixer.init()
m_dir = "music/"
songs = ["Second Chance.wav", "5.mp3", "4.mp3"]
i = 0

def start_queue(e, t):
    global i
    pygame.mixer.music.load(m_dir + songs[i])
    pygame.mixer.music.play(i)
    
    while True:
        if not pygame.mixer.music.get_busy():
            if i < len(songs) - 1:
                i += 1
            else:
                i = 0
            pygame.mixer.music.load(m_dir + songs[i])
            pygame.mixer.music.play(0)
        time.sleep(0.5)

def play():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
        

def next_song():
    global i
    if i < len(songs) - 1:
        i += 1
    else:
        i = 0
    pygame.mixer.music.load(m_dir + songs[i])
    pygame.mixer.music.play(0)

def prev_song():
    global i
    if i == 0:
        i = len(songs)-1
    else:
        i -= 1
    pygame.mixer.music.load(m_dir + songs[i])
    pygame.mixer.music.play(0)

    
### start the player in it's own thread


e = threading.Event()
t = threading.Thread(name='thread', target=start_queue, args=(e, 2))
t.start()
    
###

class PlayResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True
        e.set()
        self.notify()

    def notify(self):
        log.msg('PlayResource: ')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        print 'PUT payload: ' + request.payload
        payload = "Now playing music."
        response = coap.Message(code=coap.CHANGED, payload=payload)
        play()
        return defer.succeed(response)

class NextResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify()

    def notify(self):
        log.msg('NextResource: ')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        print 'PUT payload: ' + request.payload
        payload = "Playing next song."
        response = coap.Message(code=coap.CHANGED, payload=payload)
        next_song()
        return defer.succeed(response)

class PrevResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify()

    def notify(self):
        log.msg('PrevResource: ')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        print 'PUT payload: ' + request.payload
        payload = "Playing previous song."
        response = coap.Message(code=coap.CHANGED, payload=payload)
        prev_song()
        return defer.succeed(response)

# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()


###IOT addition

play = PlayResource()
root.putChild('play', play)

next_res = NextResource()
root.putChild('next', next_res)

prev = PrevResource()
root.putChild('prev', prev)

###

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
