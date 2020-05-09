import random, pygame, sys, threading
from pygame.locals import *
import numpy as np
import math
def handle_event(self):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

pygame.init()
FPSCLOCK = pygame.time.Clock()
DISPLAYSURE = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Test')
pxarray = pygame.PixelArray(DISPLAYSURE)
print(pxarray.shape)
angel=90*math.pi/180
print(math.cos(angel),math.sin(angel))
