import pygame
import time

pygame.init()
pygame.mixer.init()

if pygame.mixer:
    pygame.mixer.music.load('Second Chance.wav')
    pygame.mixer.music.play(1, 0.0)

while True:
    time.sleep(10)
    print("playing")
