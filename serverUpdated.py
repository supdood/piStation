
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
currentSong = ""
songSep = 0
repeatFlag = False
paused = False
listOfSongs = ["Second Chance.wav", "3.mp3", "4.mp3", "5.mp3"]
repeat = "true"
stopIndict = False
###

#play a song from the front of the queue
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
        
    def render_GET(self, request):  
        print "GET payload:  " + currentSong
        pMessage = "Now Playing: " + currentSong
        response = coap.Message(code=coap.CONTENT, payload=pMessage)
        return (defer.succeed(response))
    
    def render_PUT(self, request):
        global UNQueue
        global songSep
        global currentSong
        global nextSong
        global stopIndict
        print 'PUT payload: ' + request.payload
        if(stopIndict == False):        #if the song wasn't previously stopped, play the stopped song
            nextSep = UNQueue.find(',')
            nextSong = UNQueue[0:nextSep]
            currentSong = nextSong
            if(currentSong == ""):  #if their is no current song playing 
                if(UNQueue == ""):   #if queue is empty
                    currentSong = listOfSongs[randint(0,3)]  #select a random song from library
                else:                                        #or find the next song based on delminter postion
                    songSep = UNQueue.find(",")
                    currentSong = UNQueue[0:songSep]
            
            pygame.mixer.music.load(currentSong)            #load and play song
            pygame.mixer.music.play(1, 0.0)
            if(repeatFlag == True):                 #update queue according to repeatFlag
                UNQueue = UNQueue[(songSep + 1):] + (currentSong + ",")
            elif(repeatFlag == False):
                UNQueue = UNQueue[(songSep + 1):]
            response = coap.Message(code=coap.CHANGED, payload="Random Song")
        else:
            stopIndict = False
            pygame.mixer.music.load(currentSong)            #load and play song
            pygame.mixer.music.play(1, 0.0)
            response = coap.Message(code=coap.CHANGED, payload=("Playing: " + currentSong))
        return defer.succeed(response)

#pause and unpause the music player
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
        global paused
        print 'PUT payload: ' + request.payload
        if(paused == False):    #if song is playing, pause it
            payload = "Music paused."
            paused = True
            response = coap.Message(code=coap.CHANGED, payload=payload)
            pygame.mixer.music.pause()
        else:                   #if song is paused, resume it
            payload = "Music unpaused"
            response = coap.Message(code=coap.CHANGED, payload=payload)
            pygame.mixer.music.unpause()
        return defer.succeed(response)
    
#add a song to the queue to be played
class addToQueueResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify

    def notify(self):
        log.msg('addToQueueResource: ')
        self.updateState()
        reactor.callLater(60, self.notify)

    def render_PUT(self, request):
        global UNQueue
        print 'PUT payload: ' + request.payload
        payload = 'Next song: ' + request.payload
        addSong = request.payload
        for song in listOfSongs:
            if(addSong == song):   #if the song exists, put it in the queue
                UNQueue = UNQueue + (addSong + ",")
                response = coap.Message(code=coap.CHANGED, payload=payload)
                return defer.succeed(response)
            else:                   #if not send error message
                response = coap.Message(code=coap.CHANGED, payload="There is no song containing this name")
        return defer.succeed(response)
    
    #display the next song to be played
    def render_GET(self, request):
        global UNQueue
        print "GET payload:  " + UNQueue
        sep = UNQueue.find(",")
        displaySong = UNQueue[0:sep]
        response = coap.Message(code=coap.CONTENT, payload=(UNQueue + " / Next song: " + displaySong))
        return (defer.succeed(response))
    
#stop the music; this doesn't 
class StopResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True
        self.notify
        
    def notify(self):
        log.msg('StopResource: ')
        self.updateState()
        reactor.callLater(60, self.notify)
        
    def render_PUT(self, request):
        global stopIndict
        print 'STOP' + request.payload
        pygame.mixer.music.stop()
        response = coap.Message(code=coap.CHANGED, payload="Stopping music")
        stopIndict = True
        return (defer.succeed(response))
    
#toggle whether or not the queue will delete songs from itself or loop them   
class RepeatResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True
        self.notify
        
    def notify(self):
        log.msg('RepeatResource: ')
        self.updateState()
        reactor.callLater(60, self.notify)
        
    def render_PUT(self, request):
        global repeatFlag
        if(repeatFlag == False):    #turn on repeat
            repeatFlag = True
            response = coap.Message(code=coap.CHANGED, payload="Repeat is now enabled")
            return (defer.succeed(response))
        else:                       #turn of repeat
            repeatFlag = False
            response = coap.Message(code=coap.CHANGED, payload="Repeat is now disabled")
            return (defer.succeed(response))

    def render_GET(self, request):  #get a message saying wheter repeat is on or off
        if(repeatFlag == True):
            response = coap.Message(code=coap.CHANGED, payload="Repeat is on")
        else:
            response = coap.Message(code=coap.CHANGED, payload="Repeat is off")
        return(defer.succeed(response))
    
#skip the current song and move to the next one in the queue; update queue according to repeatFlag
class SkipResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True
        self.notify
        
    def notify(self):
        log.msg('SkipResource: ')
        self.updateState()
        reactor.callLater(60, self.notify)
        
    def render_PUT(self, request):
        global UNQueue
        global repeatFlag
        global songSep
        global currentSong
        if(UNQueue == ""):  
            currentSong = listOfSongs[randint(0,3)] #choose random song if queue is empty
        else:
            songSep = UNQueue.find(",")
            currentSong = UNQueue[0:songSep]
        if(repeatFlag == True):
            UNQueue = UNQueue[(songSep + 1):] + (currentSong + ",")
        elif(repeatFlag == False):
            UNQueue = UNQueue[(songSep + 1):]
        pygame.mixer.music.load(currentSong)
        pygame.mixer.music.play(1, 0.0)
        response = coap.Message(code=coap.CHANGED, payload="")
        return defer.succeed(response)
    
# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()


###IOT addition
pause = PauseResource()
root.putChild('pause', pause)

play = PlayResource()
root.putChild('play', play)

stop = StopResource()
root.putChild('stop', stop)

addToQueue = addToQueueResource()
root.putChild('add', addToQueue)

repResource = RepeatResource()
root.putChild('repeat', repResource)

skip = SkipResource()
root.putChild('skip', skip)
###

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
