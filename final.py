import pyglet

song1 = pyglet.media.load('1.wma')
song2 = pyglet.media.load('2.wma')
song3 = pyglet.media.load('3.mp3')
song4 = pyglet.media.load('4.mp3')
song5 = pyglet.media.load('5.mp3')

player = pyglet.media.Player()

player.queue(song1)
player.queue(song2)
player.queue(song3)
player.queue(song4)
player.queue(song5)

player.play()

while True:
    command = input('Command: ')
    if command == "pause":
        player.pause()
    elif command == "play":
        player.play()
    elif command == "next":
        player.next()
    