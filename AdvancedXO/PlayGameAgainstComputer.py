import pygame, sys, random, time, json
from pygame.locals import *
#import pandas as pd
#import numpy as np

#Load moves dictionary from json file---------------------------------------------------------------------------
try:
    boards
except NameError:
    with open('./RLGameMoves.json') as f:
        boards = json.load(f)

#Set the board and piece models' addresses --------------------------------------------------------------------------------------------------
WhitePiecePicFile = './WhitePiece50.png'
BlackPiecePicFile = './BlackPiece50.png'
BoardPicFile = './boardBR.png'
#---------------------------------------------------------------------------------------------------------------
BoardPositionsX=[130,390,649,210,390,566,290,390,489,130,210,290,489,566,649,290,390,489,210,390,566,130,390,649]
BoardPositionsY=[140,140,140,219,219,219,298,298,298,397,397,397,397,397,397,498,498,498,577,577,577,659,659,659]
#---------------------------------------- lines: position your pieces to win --------------------------------------
lines = [[0,1,2],[3,4,5],[6,7,8],[9,10,11],[12,13,14],[15,16,17],[18,19,20],[21,22,23], #horizontals
         [0,9,21],[3,10,18],[6,11,15],[1,4,7],[16,19,22],[8,12,17],[5,13,20],[2,14,23], #verticals
         [0,3,6],[2,5,8],[15,18,21],[17,20,23]]                                         #diagonals
# ---------------------------------------- Check Board Function ----------------------------
def checkboard(boardstr):
    """ this function takes a board string and evaulates the board
     Returns : [0]Open Status = True/False , [1]Board Description
    """
    for line in lines:
        if ''.join([boardstr[i] for i in line]) == 'www': 
            return False , 'white wins! ' + str(line)+ boardstr
        elif ''.join([boardstr[i] for i in line]) == 'bbb':
            return False , 'black wins! ' + str(line)+ boardstr
        elif boardstr.find('-')<0:
            return False , 'Draw! ' + boardstr
    return True, 'Unfinished Game!'
# ---------------------------------------- AI Move Function ----------------------------
def AIMove(BoardsDict,Boardstr,Turn,RandomMoveChance):
    """ Gets the move dictionary, current board str and turn, and determines a move:
        1- Simply tries the maximum value in the moves
        2- if not found, simply tries a random move
    """
    #to check for obvious moves. For example avoiding obvious losses or place the only remaining piece to complete the line and win.
    #this also helps to reduce move dictionary size
    for line in lines:
        #play to win
        if ([Boardstr[i] for i in line].count('-') == 1) & ([Boardstr[i] for i in line].count(Turn)==2): #find lines where player can win
            lineindex = [Boardstr[i] for i in line].index('-') #find the only remaining cell to put the piece in
            return Boardstr[:line[lineindex]] + Turn + Boardstr[line[lineindex]+1:]
        #play the obvious not to lose
        #'w' if Turn=='b' else 'b'
    for line in lines:
        if ([Boardstr[i] for i in line].count('-') == 1) & ([Boardstr[i] for i in line].count('w' if Turn=='b' else 'b')==2): #find lines where player can avoid loses
            lineindex = [Boardstr[i] for i in line].index('-') #find the only remaining cell to put the piece in
            return Boardstr[:line[lineindex]] + Turn + Boardstr[line[lineindex]+1:]
    
    if random.random() <= RandomMoveChance:    #play randomly to explore possible new moves
        #select a random cell from available cells
        cell = random.choice([i for i, ltr in enumerate(Boardstr) if ltr == '-'])
        #update table string
        return Boardstr[:cell] + Turn + Boardstr[cell+1:]    
    else:    
        try:
            return max(BoardsDict[Boardstr].items(), key = lambda x: x[1])[0]
        except:
            #select a random cell from available cells
            cell = random.choice([i for i, ltr in enumerate(Boardstr) if ltr == '-'])
            #update table string
            return Boardstr[:cell] + Turn + Boardstr[cell+1:]
# ---------------------------------------- Pieces class ----------------------------
class Piece(pygame.sprite.Sprite):
    """ This class represents the pieces.It derives from the "Sprite" class in Pygame."""
    def __init__(self,color):
        """ Constructor. Pass in the color of the piece"""
        super().__init__()
        if color== 'w':
            self.image = pygame.image.load(WhitePiecePicFile).convert_alpha()
        elif color == 'b':
            self.image = pygame.image.load(BlackPiecePicFile).convert_alpha()
        self.rect = self.image.get_rect()

pygame.init()
screen = pygame.display.set_mode((800,800))
#screen.fill((255,255,255))

Rematch = True # if Faslse will exit the game entirely. If True user can press space to play another game
running = True # loop controller to run a single match
ResetBoard = True #Flag to reset the board each time the program runs. as well as each time rematatch being initiated
pygame.mouse.set_visible(False) #hides the mouse pointer

while Rematch:
    if ResetBoard == True:
        BoradIMG = pygame.image.load(BoardPicFile)
        screen.blit(BoradIMG, (0,0))

        #pygame.draw.circle(screen, pink, (130,140), 25, 25)
        #pygame.draw.lines(screen, color, closed, pointlist, thickness)
        #pygame.draw.lines(screen, black, False, [(100,100), (150,200), (200,100)], 1)

        #This is a list of all pieces sprites
        block_list = pygame.sprite.Group()

        # This is a list of every sprite including the mouse spirite
        all_sprites_list = pygame.sprite.Group()

        '''
        def DrawBoard(boardstr):
            """ Only used to initiate a board for development testing and QA
            """
            for i in range(24):
                if boardstr[i] != '-':
                    Pieces = Piece(boardstr[i])
                    Pieces.rect.x = BoardPositionsX[i] -24
                    Pieces.rect.y = BoardPositionsY[i] -22
                    all_sprites_list.add(Pieces)
        boardstr = '-bwwwbb-bb--wbwwbwwbw-b-'
        DrawBoard(boardstr)
        '''

        clock = pygame.time.Clock() # Used to manage how fast the screen updates
        boardstr = '-'*24 #game always starts with an empty board
        turn = 'w' # game always starts with white turn
        AIPick = 'w' if random.random()<=.5 else 'b' # w indicates AI plays white, b black

        PlayerPieceMouse = Piece(turn)
        screen.blit(PlayerPieceMouse.image, PlayerPieceMouse.rect)

        all_sprites_list.add(PlayerPieceMouse)

        pygame.font.init() # you have to call this at the start, if you want to use this module.
        myfont = pygame.font.SysFont('Comic Sans MS', 30)

        pygame.display.update()

        starttime = time.time() # set the game timer for current game
        ResetBoard = False #to ensure the board will not have to unnecessarily refresh on tick
        
    while (running) & (checkboard(boardstr)[0]):
        #pygame.display.update()
        if AIPick==turn:
            AImoveBoard = AIMove(BoardsDict= boards,Boardstr = boardstr,Turn=turn,RandomMoveChance=0) #AI selects the move and returns the new board
            AIplayedpos=[i for i in range(24) if AImoveBoard[i] != boardstr[i]][0] #returns the position which AI played
            Pieces = Piece(turn) # This represents a piece that AI is about to place
            # Set the piece location
            Pieces.rect.x = BoardPositionsX[AIplayedpos] -24
            Pieces.rect.y = BoardPositionsY[AIplayedpos] -22
            # Add the block to the list of objects
            #block_list.add(block)
            all_sprites_list.add(Pieces)
            #update drawboard
            boardstr = AImoveBoard
            #change turn
            turn = 'b' if turn=='w' else 'w'
            #change mouse view model based on whose turn is it
            PlayerPieceMouse.image = pygame.image.load(WhitePiecePicFile if turn=='w' else BlackPiecePicFile).convert_alpha()

        pos=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif pygame.key.get_pressed()[K_ESCAPE]: #event.type == 2: #Press Escape to exit
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #event.type == 5: #mouse left button down (1: Left-click , 2= Middle-click , 3=Right-click)

                for i in range(24):
                    if ((pos[0]-BoardPositionsX[i])**2 + (pos[1]-BoardPositionsY[i])**2 <= 625) & (boardstr[i]== '-'): #read which cell is being clicked on
                        # This represents a piece to place
                        Pieces = Piece(turn)

                        # Set the piece location
                        Pieces.rect.x = BoardPositionsX[i] -24
                        Pieces.rect.y = BoardPositionsY[i] -22

                        # Add the block to the list of objects
                        #block_list.add(block)
                        all_sprites_list.add(Pieces)

                        #update drawboard
                        boardstr = boardstr[:i] + turn + boardstr[i+1:]

                        #change turn
                        turn = 'b' if turn=='w' else 'w'

                        #change mouse view model based on whose turn is it
                        PlayerPieceMouse.image = pygame.image.load(WhitePiecePicFile if turn=='w' else BlackPiecePicFile).convert_alpha()


    #         else:
    #             print(event.type)
        #pygame.display.update()
        screen.blit(BoradIMG, (0,0))
        textsurface = myfont.render(str(pos), False, (0, 0, 0))
        screen.blit(textsurface,(0,0))

        textsurface = myfont.render(('Black' if turn=='b' else 'White') + '\'s turn!', False, (0, 0, 0))
        screen.blit(textsurface,(300,50))

        hours, rem = divmod(time.time() - starttime, 3600)
        minutes, seconds = divmod(rem, 60)
        textsurface = myfont.render( '{:0>2}:{:0>2}:{:04.1f}'.format(int(hours),int(minutes),seconds), False, (0, 0, 0))
        screen.blit(textsurface,(630,0))

        PlayerPieceMouse.rect.x = pos[0] - 22
        PlayerPieceMouse.rect.y = pos[1] - 20

        # Draw all the spites
        all_sprites_list.draw(screen)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 60 frames per second
        clock.tick(60)
    #this is to make sure game won't rerun itself after it concluded
    running = False
    # This code block refreshes the screen and show who won along with winning line! (or Draw)
    screen.blit(BoradIMG, (0,0))
    textsurface1 = myfont.render(checkboard(boardstr)[1], False, (0, 0, 0))
    screen.blit(textsurface1,(100,0))
    textsurface1 = myfont.render('Press Space for Rematch or Escape to Exit!', False, (0, 0, 0))
    screen.blit(textsurface1,(100,50))
    all_sprites_list.draw(screen)
    pygame.display.flip()


    # user can press space to request rematch
    for event in pygame.event.get():
        if (event.type == pygame.QUIT) | (pygame.key.get_pressed()[K_ESCAPE]):
            Rematch = False
        elif pygame.key.get_pressed()[K_SPACE]:
            running = True #initiate another match
            ResetBoard = True
            try:
                del all_sprites_list, PlayerPieceMouse#, myfont, textsurface, textsurface1, clock , BoradIMG
            except:
                True
pygame.quit()
#sys.exit()
del all_sprites_list, PlayerPieceMouse
