import binascii
import time
from timeit import default_timer as timer
import random
import pygame.gfxdraw



class Memory:

    def __init__(self,pygame,window,rects): #need to use pygame commands and window
        self.system_mem = [0] * 4096  # onboard memory
        # registiierrs <finnish>
        self.gpio = [0] * 16 #chip-8 has sixteen 8-bit registers
        self.index_reg = 0  # 16 bit index register. Refered to as I
        #print("wot is iR ", type(self.index_reg))
        self.PC = 0x200  # he program counter (PC) should be 16-bit, and is used to store the currently executing address.
        self.stack = []
        #16 data registers
        self.registers =[0]*16
        self.VX = [0]*16

        #defining pygame
        self.pygame = pygame
        self.window = window
        self.rects = rects
        #self.sqr =  u'\u23F9'
        self.sqr = '#'
        self.y_offset = self

                    #________________stack___________________#
        #The stack is only used to store return addresses when subroutines are called.
        #includes the address of the topmost stack element. The stack has at most 16 elements in it at any given time
        #Since we're doing this in python, which has a list that we can just pop/append to, we can ignore this. In python, just make a list

        # display
        self.rows, self.cols = (70, 68)
        self.buffer = [[" " for i in range(self.cols)] for j in range(self.rows)]
        self.pixels = [[" " for i in range(self.cols)] for j in range(self.rows)]
        self.display = [0] * 340 * 338
        self.key_inputs = [0] * 16
        self.delay_timer = 0
        self.sound_timer = 0
        self.should_draw = False
        self.F = open
        self.x_coord = 0
        self.prev_X = 0
        self.y_coord = 0
        self.y_offset = 0


        # sprites usually stored at 050–09F
        self.zero = [0xF0, 0xF0, 0x90, 0x90, 0xF0]
        self.one =  [0x20, 0x60, 0x20, 0x20, 0x70]
        self.two = [0xF0, 0x10, 0xF0, 0x80, 0xF0]
        self.three = [0xF0, 0x10, 0xF0, 0x10, 0xF0]
        self.four = [0x90, 0x90, 0xF0, 0x10, 0x10]
        self.five =[0xF0, 0x80, 0xF0, 0x10, 0xF0]
        self.six =[0xF0, 0x80, 0xF0, 0x90, 0xF0]
        self.seven =[0xF0, 0x10, 0x20, 0x40, 0x40]
        self.eight =[0xF0, 0x90, 0xF0, 0x90, 0xF0]
        self.nine =[0xF0, 0xF0, 0xF0, 0x10, 0xF0]

        self.A = [0xF0, 0x90, 0xF0, 0x90, 0x90]
        self.B = [0xE0, 0x90, 0xE0, 0x90, 0xE0]
        self.C = [0xF0, 0x80, 0x80, 0x80, 0xF0]
        self.D = [0xE0, 0x90, 0x90, 0x90, 0xE0]
        self.E = [0xF0, 0x80, 0xF0, 0x80, 0xF0]
        self.F = [0xF0, 0x80, 0xF0, 0x80, 0x80]

        self.system_mem[0x050] = 0xF0
        self.system_mem[0x051] = 0xF0
        self.system_mem[0x052] = 0x90
        self.system_mem[0x053] = 0x90
        self.system_mem[0x054] = 0xF0

        self.pygame = pygame
        self.window = window



    #pygame draw function called from DXYN
    def draw(self,height,start_time):
        print("")

        # debug code
        print( hex(self.x_coord) ," ",  hex(self.y_coord) )
        bits = [0]*8
        self.y_coord = self.y_coord*6  #write now this is
        self.x_coord = self.x_coord*6


        #change!
        for y in range(height):
            print("testing offset ", self.y_offset)
            a = self.x_coord

            dereferenced_I = self.system_mem[self.index_reg + y]  # move to next row pixel
            #print(bin(dereferenced_I))
            for i in range(8):
                bits[7-i] = 1 if dereferenced_I & 1 else 0 #7-i is used because bits are being shifted off the end into the container "bits"
                dereferenced_I = dereferenced_I >> 1

            for x in range(8):

                if bits[x] == 1:

                    self.pygame.draw.rect(self.window, (233, 21, 123), (a, self.y_coord , 5, 5))
                    #print("b is ", b)
                    a += 5
                    start = timer()
                    print("start time", start)
                    end = timer()
                    dif = end - start
                    while dif < (1/60):
                        end = timer()
                        dif = end - start
                    pygame.display.flip()
                else:
                    a +=5 #ensures the correct pixel drawing for 0's decoded from index_reg
                    #print("drawing ", hex(self.x_coord) )

            self.y_offset +=5 # needed to draw additional rows
            if self.y_offset % 20 == 0:
                self.y_offset = 0
            for r in self.buffer:
                for c in r:
                    print(c, end=" ")
                print()





    def emulateCycle(self,start_time,rects):

        '''' game_dat is the first byte of game file. This line here efftively 
        loads the game into system memory'''''

        # *************Fetch Opcode*************** "the instruction from memory at the current PC (program counter)"
        self.opcode = self.system_mem[self.PC]  # memory[0,1,2,3,...,0x200,...,0x1000]

        # ************* Decode ******************
        self.opcode = self.system_mem[self.PC] << 8 | self.system_mem[self.PC + 1] #increase pc by 1.
        extracted_op = self.opcode & 0xF000

        #***************************************OPCODES***************************************#


        #00EE
        if(self.opcode == 0x00EE): # Returns from a subroutine.
            # The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.
            print("calling subroutine at ", hex(self.opcode & 0x0FFF), "and returning to address in self.index_reg", hex(self.index_reg))
            self.PC = self.stack.pop() +2
            #print("PC = ", hex(self.PC))


        #0xE0
        elif self.opcode == 0x00E0: #clean screen
            print("working with opcode ", hex(self.opcode))
            print("########################################################")
            for i in self.buffer:
                self.buffer = 0
            self.PC +=2

        # 1NNN
        elif (extracted_op  ==0x1000): #Jumps to address NNN.
            print("working with opcode ", hex(self.opcode))
            self.PC = self.opcode &0x0FFF
            print("jumping to opcode ", hex(self.PC) )



        #2NNN
        elif (extracted_op == 0x2000):   #Calls subroutine at NNN.
             #The stack is only used to store return addresses when subroutines are called.
             print("working with opcode ", hex(self.opcode))
             print("calling subroutine at ", hex(self.opcode & 0x0FFF))
             self.stack.append(self.PC)
             self.PC = self.opcode & 0x0FFF # how can this be. PC is only 12 bits and opcode is 16. not after line 79 it aint
             print("what is in pc?" , hex(self.PC))


        #3XNN
        elif (extracted_op == 0x3000): # Skips the next instruction if VX equals NN. (Usually the next instruction is a jump to skip a code block);
            print("working with opcode ", hex(self.opcode))
            if(self.VX[self.opcode >> 8 & 0x0F ] == self.opcode & 0x00FF):
                # 0x3takes this route
                self.PC += 4 # must be 4.
            # todo find out why else needs to be self.PC +=4. F3 OK is F3 NO if this is present
            else:
                print("next instruction")
                self.PC += 2

        #4XNN NN= 2a
        elif extracted_op == 0x4000:  #Skips the next instruction if VX does not equal NN. (Usually the next instruction is a jump to skip a code block);
            print("working with opcode ", hex(self.opcode))
            if self.VX[self.opcode >> 8 & 0x0F] != self.opcode & 0x00FF:
                print("Vx contains = ", hex(self.VX[self.opcode >> 8 & 0x0F]) )
                self.PC += 4 #0x7 takes this route
            else:
                # 0x4 takes this route
                self.PC += 2

        #5XY0
        elif (extracted_op == 0x5000): #Skips the next instruction if VX equals VY. (Usually the next instruction is a jump to skip a code block)
            print("working with opcode $# ", hex(self.opcode))
            print(self.opcode >> 8 & 0x0F,"   ", self.VX[self.opcode >> 4 & 0x00F])
            if self.VX[self.opcode >> 8 & 0x0F] == self.VX[self.opcode >> 4 & 0x00F]:
                self.PC += 4
            else:
                self.PC += 2 # 0x5 takes this route

        #6XNN
        elif (extracted_op == 0x6000): #Sets VX to NN.
            print("working with opcode ", hex(self.opcode))
            self.VX[self.opcode >>8 & 0x0F] = self.opcode & 0x00FF #this translate to VX[register_number]
            self.PC += 2

        #7XNN THIS IS BEHIND BY 2 COUNTS
        elif (extracted_op == 0x7000): #Const	Vx += N	Adds NN to VX. (Carry flag is not changed);
            print("working with opcode ", hex(self.opcode))
            self.VX[self.opcode >> 8 & 0x0F] += (self.opcode & 0x00FF)
            self.PC += 2

        #8XY_
        elif (extracted_op == 0x8000):  # Const	Vx += N	Adds NN to VX. (Carry flag is not changed);
            print(" 0x8_ working with opcode ", hex(self.opcode))
            determn_bit = self.opcode & 0x000F
            print("determn_bit is", hex(determn_bit))

            if determn_bit == 0x0: #Sets VX to the value of VY.
                #print("working with opcode ", hex(self.opcode), " x = ", hex(self.opcode >>8 & 0x0F), " y = ",hex(self.opcode >>4 & 0x00F) ) YATTA
                self.VX[self.opcode >> 8 & 0x0F] = self.VX[self.opcode >> 4 & 0x00F]
                self.PC += 2

            elif determn_bit == 0x1: #sets VX to bitwise or op of VX and VY
                self.VX[self.opcode >> 8 & 0x0F] = self.VX[self.opcode >> 8 & 0x0F] | self.VX[self.opcode >> 4 & 0x00F]
                self.PC += 2

            elif determn_bit == 0x2: #Sets VX to VX and VY. (Bitwise AND operation);
                self.VX[self.opcode >> 8 & 0x0F] = self.VX[self.opcode >> 8 & 0x0F] & self.VX[self.opcode >> 4 & 0x00F]
                self.PC += 2

            elif determn_bit == 0x3: #Sets VX to VX xor VY.
                self.VX[self.opcode >> 8 & 0x0F] = self.VX[self.opcode >> 8 & 0x0F] ^ self.VX[self.opcode >> 4 & 0x00F]
                self.PC += 2

            elif determn_bit == 0x4: #Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.
                self.VX[self.opcode >> 8 & 0x0F] += self.VX[self.opcode >> 4 & 0x00F]
                sum = self.VX[self.opcode >> 8 & 0x0F] + self.VX[self.opcode >> 4 & 0x00F]
                if sum > 255:
                    self.VX[0x0F] = 1
                    self.PC +=2
                elif sum < 255:
                    self.VX[0x0F] = 0
                    self.PC += 2
            #0x8XYD
            elif determn_bit == 0x5: #	VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there is not.
                diff = self.VX[self.opcode >> 8 & 0x0F] - self.VX[self.opcode >> 4 & 0x00F]
                print("Vx = ", hex(self.opcode >> 8 & 0x0F))
                print("Vy= ", hex(self.opcode >> 4 & 0x00F))
                self.VX[self.opcode >> 8 & 0x0F] -= self.VX[self.opcode >> 4 & 0x00F]
                if diff < 0: #borrow flag is used when Vy is bigger than Vx
                    self.VX[0xF] = 1
                    self.PC += 2
                else:
                    self.VX[0xF] = 0
                    self.PC += 2

            elif determn_bit == 0x6: #Stores the least significant bit of VX in VF and then shifts VX to the right by 1
               #big endian" most sig bit is at lowest memory position
               print("working with opcode ", hex(self.opcode))
               print("hmmmmmmmmmmmmmmm?")
               print("Vx =", bin(self.VX[self.opcode >> 8 & 0x0F]))
               lest_bit = 1 if self.VX[self.opcode >>8 & 0x0F] & 1 else 0 #define least significant bit
               self.VX[0xF] = lest_bit #store least sig bit into VX
               print(bin(self.VX[self.opcode >> 8 & 0x0F]))
               self.PC +=2

            elif determn_bit == 0x7:
                pass
            elif determn_bit == 0xE: #	Stores the most significant bit of VX in VF and then shifts VX to the left by 1.[b]
                #If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
                print("VX before bit shift ", bin(self.VX[self.opcode >> 8 & 0x0F]) )
                print("VF before assignment ", self.VX[0x0F])
                self.VX[0x0F] = self.VX[self.opcode >> 8 & 0x0F] >> 1  #store most sig bit in VX
                self.VX[self.opcode >> 8 & 0x0F] = self.VX[self.opcode >> 8 & 0x0F] >> 1
                print("VX after bit shift ", bin(self.VX[self.opcode >> 8 & 0x0F]))
                print("VF after assignment ", self.VX[0x0F])
                self.PC +=2

        #9XY0
        elif (extracted_op == 0x9000): #Skips the next instruction if VX does not equal VY.
            print("working with opcode ", hex(self.opcode))
            if self.VX[self.opcode >> 8 & 0x0F] != self.VX[self.opcode >> 4 & 0x00F]:
                self.PC += 4
            else:
                self.PC += 2


        #ANNN
        elif (extracted_op == 0xA000):  # Sets I to the address NNN.
            print("working with opcode ", hex(self.opcode))
            self.index_reg = self.opcode & 0x0FFF
            #print("index reg type is $$$$ ", type(self.index_reg))
            self.PC += 2

        #CXNN
        elif(extracted_op == 0xC000): #Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
            print("working with opcode ", hex(self.opcode))
            rand_mask = random.randrange(0,256)
            # register                        =  0xNN                   & random num(0,255)
            self.VX[self.opcode >> 8 & 0x0F ] = (self.opcode & 0x00FF ) & rand_mask
            print("cxnn yeilds ", hex(self.VX[self.opcode >> 8 & 0x0F ]))
            self.PC += 2


        #DXYN
        #calls pygame draw function
        elif(extracted_op == 0xD000):# Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels
            print("working with opcode ", hex(self.opcode))
            self.x_coord = self.VX[self.opcode >> 8 & 0x0F] #Vx
            self.y_coord = self.VX[self.opcode >> 4 & 0x00F] #vy
            self.PC += 2
            height = self.opcode & 0x000F
            self.draw(height,start_time)

            return self.rects

        #EXA1, EX9E
        elif extracted_op == 0xE000: #Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block);
            #skipping implementation for now because I dont have key functionality.
            #for now it will just be self.pc += 4 since the key will not be pressed
            if self.opcode & 0x00F == 0x00A0:
                print("working with opcode ", hex(self.opcode))
                self.PC +=2 #changed 12/26 to +=2 from +=4
            else:
                self.PC +=2

        elif extracted_op == 0xF000:
            extrctd_bit = self.opcode & 0x0FF
            print("extrctd_bit ",hex(extrctd_bit))

            #FX07
            #Set VX = delay timer
            #important for ball
            self.VX[self.opcode >> 8 & 0x0F] = self.delay_timer
            self.PC += 2

            #FX0A
            #FX15
            #set delay timer = VX
            if extrctd_bit == 0x15:
                self.delay_timer = self.VX[self.opcode >>8 & 0x0F]
                self.PC += 2
            #FX18
            #FX1E


            #FX29
            #set I = location of sprite for digit VX
            if extrctd_bit == 0x29:
                self.index_reg = self.system_mem[self.VX[self.opcode >> 8 & 0x0F]]
                self.PC += 2

            #FX33
            #Stores the binary-coded decimal representation of VX, with the hundreds digit
            # in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.
            if extrctd_bit == 0x33:
                print("self.index_reg: ", self.index_reg)
                print("VX contains ", (self.VX[self.opcode >> 8 & 0x0F]))
                temp = [int(i) for i in str(self.VX[self.opcode >> 8 & 0x0F])] #r is a list that holds the values of VX in as int
                for i in range(0,len(temp)):
                    #print("storing BCD interpretation of ", temp[i], "/", bin(temp[i]) )
                    self.system_mem[self.index_reg+i] =temp[i]
                print("self.index_reg: ", self.index_reg)
                self.PC += 2
                print("311? ", self.index_reg)

            #FX55
            if extrctd_bit == 0x55:
                # Store registers V0 through Vx in memory starting at location I.
                # The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
                print("$opcode ", hex(self.opcode), " range ", 0," to ", hex(self.opcode >> 8 & 0x0F))
                for i in range(0, self.opcode >> 8 & 0x0F):
                    self.system_mem[self.index_reg+i] = self.VX[i]
                self.PC += 2

            #FX65
            if extrctd_bit == 0x65:
                # Read registers V0 through Vx from memory starting at location I.
                # The interpreter reads values from memory starting at location I into registers V0 through Vx.
                print("%opcode ", hex(self.opcode), " range ", hex(self.index_reg), " to ", hex(self.opcode >> 8 & 0x0F))
                for i in range(self.index_reg, self.opcode >>8 & 0x0F):
                    self.VX[i] = self.system_mem[self.index_reg + i]
                self.PC += 2

        else:
            print("Unknown instruction: %X" % self.opcode)
            print("extracted_op ", extracted_op)
            return self.rects



        # Update timers
    def loadGame(self):    #22fc 6b0c == 34 252 107 12
            #changex

            #filename ='test_opcode.ch8'
            filename = 'pong2.c8'
            game_data = open(filename, "rb").read()
            read_file = 0 #used to increment through chip8 file
            while read_file < len(game_data):
                self.system_mem[0x200 + read_file] = (game_data[read_file])
                #print(ord(game_data[offset]))
                read_file += 1



            #with open(filename, 'rb') as f:
                #for chunk in iter(lambda: f.read(32), b''):
                #print chunk.encode('hex')

                # game_data= binascii.hexlify(f.read())
                # print(binascii.hexlify(game_data))
