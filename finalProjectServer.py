import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap


class SongResource (resource.CoAPResource):
    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.songName = ""
        self.addParam(resource.LinkParam("title", "Song Resource"))

    def render_GET(self, request):
        payload = self.name
        response = coap.Message(code = coap.CONTENT, payload= payload)
        return defer.succeed(response)

class CoreResource(resource.CoAPResource): #taken from the txThings example
    """
    Example Resource that provides list of links hosted by a server.
    Normally it should be hosted at /.well-known/core

    Resource should be initialized with "root" resource, which can be used
    to generate the list of links.

    For the response, an option "Content-Format" is set to value 40,
    meaning "application/link-format". Without it most clients won't
    be able to automatically interpret the link format.

    Notice that self.visible is not set - that means that resource won't
    be listed in the link format it hosts.
    """

    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        print payload
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)



log.startLogging(sys.stdout)
root = resource.CoAPResource()

library = resource.CoAPResource()
root.putChild('Library', library)

well_known = resource.CoAPResource()
root.putChild('.well-known', well_known)
core = CoreResource(root)
well_known.putChild('core', core)

song1 = SongResource()
song1.name = "1"
library.putChild('Song 1', song1)

song2 = SongResource()
song2.name = "2"
library.putChild('Song 2', song2)

song3 = SongResource()
song3.name = "3"
library.putChild('Song 3', song3)

song4 = SongResource()
song4.name = "4"
library.putChild('Song 4', song4)

song5 = SongResource()
song5.name = "5"
library.putChild('Song 5', song5)

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))
reactor.run()





        
