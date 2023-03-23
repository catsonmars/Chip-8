print("Is this main? : {}".format(__name__))
import chip
import pygame
import time


def main():

    #init pygame
    pygame.init()
    pygame.display.set_caption("Chip 8")

    #define pygame window namne
    window = pygame.display.set_mode((640,480)) #window is a surface object
    rects = []  # list of rects "sprites" that will be drawn
    # load game into memory
    memory = chip.Memory(pygame, window,rects) #instantializes chip 8 class

    memory.loadGame()
    runProgram = True
    #while runProgram:  #pygame window loop
    while runProgram:

        #ensure 60hz display
        start = time.time()
        memory.emulateCycle(start, rects) #calls chip8 emulation

        for event in pygame.event.get(): #run pygame loop
            if event.type == pygame.QUIT:
                runProgram = False





if __name__ == "__main__":
    main()










             