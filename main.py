print("Is this main? : {}".format(__name__))
from timeit import default_timer as timer
import chip
import pygame
import time


def main():

    #init pygame
    pygame.init()
    pygame.display.set_caption("Chip 8")

    #define pygame window namne
    window = pygame.display.set_mode((640,480))
    rects = []  # list of rects "sprites" that will be drawn
    # load game into memory
    memory = chip.Memory(pygame, window,rects) #instantializes chip 8 class

    memory.loadGame()
    runProgram = True

    #def draw():
                                                #  x   y   len   height
    #    pygame.draw.rect(window, (233,21,123), (1095, 222, 100, 100))
    #while runProgram:  #pygame window loop
    for x in range(0, 2215):

        #ensure 60hz display
        start = timer()

        rects = memory.emulateCycle(start,rects) #calls chip8 emulation


        for event in pygame.event.get(): #run pygame loop
            if event.type == pygame.QUIT:
                runProgram = False





if __name__ == "__main__":
    main()





if __name__ == "__main__":
    main()










             
