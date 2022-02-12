#inspired by : https://www.youtube.com/watch?v=U4ogK0MIzqk&ab_channel=SebastianLague

import pygame, sys, random, time, json
import numpy as np
from pygame.locals import *

pieces_file = './Files/Pieces.png' #file with image of pieces
SQW = 75 #Square width
RANKS = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}


#FEN Notation: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
starting_board = 'r2q1rk1/pp2ppbp/5np1/1Ppp2B1/3PP1b1/Q1P2N2/P4PPP/3RKB1R b K c6 0 13'#'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

def setup_board(fen_string):
    """
    This will create spirites and places them in their appropriate location based on the FEN string 
    """
    parts = starting_board.split(' ')
    (fen_string, turn, castle, enpassant, n1, n2)  = (* parts,)
    spirit_group = pygame.sprite.Group()
    i = 0
    board_list = [None]*64 #creates a list that captures current board status
    for p in fen_string:
        if p == '/':
            continue
        elif p.isdigit():
            i += int(p)
        else:
            board_list[i] = p
            Pieces = Piece(p,i)
            spirit_group.add(Pieces)
            i += 1
    
    if enpassant != '-':
        enpassant = RANKS[enpassant[0]]*8 + 8 - int(enpassant[1])
    else:
        enpassant = 0
    
    return(spirit_group,board_list,enpassant,turn,castle)

def controlled_area(board,color):
    if color=='w':
        white_controlled = True
    else:
        white_controlled = False
    
    controlled_squares = []
    
    for i in [j for j in range(64) if board[j] if board[j].isupper()==white_controlled]:#if a[j] --> if not None // if board[j].isupper()==white_controlled --> checks for controlled areas by capital letters
        squares = get_possible_moves(i,board)[1]
        controlled_squares.extend(squares)
    
    controlled_squares = np.unique(controlled_squares)
    
    return(controlled_squares)



def get_possible_moves(position,board,en_passant=None,possible_castles=None):
    """ Gets a list of all possible moves for the current selected piece """
    
    if position == None:
        return([])
    
    possible_moves = []
    controlled_squares = [] #used to determine checked status. since pawn's control square is not the same as their possible move list 
    x = position %  8
    y = position // 8
    pawn_moves = {'P':{'move':[(0,-1),(0,-2)],'control':[(-1,-1),(1,-1)]},'p':{'move':[(0,1),(0,2)],'control':[(-1,1),(1,1)]}}#a bit different structure as pawns can move and control differently
    knight_moves = [(1,-2),(2,-1),(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2)]
    rook_moves = [(0,1),(0,-1),(1,0),(-1,0)]
    bishop_moves = [(1,1),(1,-1),(-1,1),(-1,-1)]
    queen_moves = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    
    if board[position] in ['P','p']:
        #Diagonally taking // controlling space
        for i in range(0,2): #indicates each of moves/control for each pawn
            if (x + pawn_moves[board[position]]['control'][i][0] >= 0 and x + pawn_moves[board[position]]['control'][i][0] <= 7 and y + pawn_moves[board[position]]['control'][i][1] >= 0 and y + pawn_moves[board[position]]['control'][i][1] <= 7):
                controlled_squares.append((y + pawn_moves[board[position]]['control'][i][1])*8 + x + pawn_moves[board[position]]['control'][i][0])
                if board[(y + pawn_moves[board[position]]['control'][i][1])*8 + x + pawn_moves[board[position]]['control'][i][0]] != None: #check if there is a piece diagonally in front of the pawn
                    if board[(y + pawn_moves[board[position]]['control'][i][1])*8 + x + pawn_moves[board[position]]['control'][i][0]].isupper() != board[position].isupper(): #make sure it is the opposite color
                        possible_moves.append((y + pawn_moves[board[position]]['control'][i][1])*8 + x + pawn_moves[board[position]]['control'][i][0])
                elif (y + pawn_moves[board[position]]['control'][i][1])*8 + x + pawn_moves[board[position]]['control'][i][0] == en_passant and (board[position]=='P' and en_passant//8==2 or board[position]=='p' and en_passant//8==5): #The pawn can attack an en passant square and it is the right side. Back attacking rank 3 and white attacking rank 6
                        possible_moves.append(en_passant)
        #Moving ahead
        for i in range(0,2): #indicates each of moves/control for each pawn

            if board[(y + pawn_moves[board[position]]['move'][i][1])*8 + x + pawn_moves[board[position]]['move'][i][0]]== None and (i==0 or i==1 and (board[position]=='p' and y==1 or board[position]=='P' and y==6)):
                possible_moves.append((y + pawn_moves[board[position]]['move'][i][1])*8 + x + pawn_moves[board[position]]['move'][i][0])
            else:
                break #if first position for pawn is taken then it will not check the second square
    elif board[position] in ['N','n']:
        for i in knight_moves:
            if (x + i[0] >= 0 and x + i[0] <= 7 and y + i[1] >= 0 and y + i[1] <= 7) and (board[(y + i[1])*8 + x + i[0]]== None or board[position].isupper() != board[(y + i[1])*8 + x + i[0]].isupper()): #first making sure that the move is within the board and the target position is either empty or is taken by the opposite color
                possible_moves.append( (y + i[1])*8 + x+i[0])
                controlled_squares.append( (y + i[1])*8 + x+i[0])
    elif board[position] in ['R','r']:
        for i in rook_moves:
            for j in range(1,8):
                if (x + i[0]*j >= 0 and x + i[0]*j <= 7 and y + i[1]*j >= 0 and y + i[1]*j <= 7) and (board[(y + i[1]*j)*8 + x + i[0]*j]== None):
                    possible_moves.append((y + i[1]*j)*8 + x+i[0]*j)
                    controlled_squares.append((y + i[1]*j)*8 + x+i[0]*j)
                elif (x + i[0]*j >= 0 and x + i[0]*j <= 7 and y + i[1]*j >= 0 and y + i[1]*j <= 7) and (board[position].isupper() != board[(y + i[1]*j)*8 + x + i[0]*j].isupper()):
                    possible_moves.append((y + i[1]*j)*8 + x+i[0]*j)
                    controlled_squares.append((y + i[1]*j)*8 + x+i[0]*j)
                    break
                else:
                    break
    elif board[position] in ['b','B']:
        for i in bishop_moves:
            for j in range(1,8):
                if (x + i[0]*j >= 0 and x + i[0]*j <= 7 and y + i[1]*j >= 0 and y + i[1]*j <= 7) and (board[(y + i[1]*j)*8 + x + i[0]*j]== None):
                    possible_moves.append((y + i[1]*j)*8 + x+i[0]*j)
                    controlled_squares.append((y + i[1]*j)*8 + x+i[0]*j)
                elif (x + i[0]*j >= 0 and x + i[0]*j <= 7 and y + i[1]*j >= 0 and y + i[1]*j <= 7) and (board[position].isupper() != board[(y + i[1]*j)*8 + x + i[0]*j].isupper()):
                    possible_moves.append((y + i[1]*j)*8 + x+i[0]*j)
                    controlled_squares.append((y + i[1]*j)*8 + x+i[0]*j)
                    break
                else:
                    break               
    elif board[position] in ['q','Q']:
        for i in queen_moves:
            for j in range(1,8):
                if (x + i[0]*j >= 0 and x + i[0]*j <= 7 and y + i[1]*j >= 0 and y + i[1]*j <= 7) and (board[(y + i[1]*j)*8 + x + i[0]*j]== None):
                    possible_moves.append((y + i[1]*j)*8 + x+i[0]*j)
                    controlled_squares.append((y + i[1]*j)*8 + x+i[0]*j)
                elif (x + i[0]*j >= 0 and x + i[0]*j <= 7 and y + i[1]*j >= 0 and y + i[1]*j <= 7) and (board[position].isupper() != board[(y + i[1]*j)*8 + x + i[0]*j].isupper()):
                    possible_moves.append((y + i[1]*j)*8 + x+i[0]*j)
                    controlled_squares.append((y + i[1]*j)*8 + x+i[0]*j)
                    break
                else:
                    break         
    elif board[position] in ['k','K']:
        for i in queen_moves:
            if (x + i[0] >= 0 and x + i[0] <= 7 and y + i[1] >= 0 and y + i[1] <= 7) and (board[(y + i[1])*8 + x + i[0]]== None):
                possible_moves.append((y + i[1])*8 + x+i[0])
                controlled_squares.append((y + i[1])*8 + x+i[0])
            elif (x + i[0] >= 0 and x + i[0] <= 7 and y + i[1] >= 0 and y + i[1] <= 7) and (board[position].isupper() != board[(y + i[1])*8 + x + i[0]].isupper()):
                possible_moves.append((y + i[1])*8 + x+i[0])   
                controlled_squares.append((y + i[1])*8 + x+i[0])

    return(possible_moves,controlled_squares)


class Piece(pygame.sprite.Sprite):
    """ This class represents the pieces.It derives from the "Sprite" class in Pygame."""
    def __init__(self,piecetype,position):
        """ Constructor. Pass in the color of the piece"""
        super().__init__()
        
        self.piecetype = piecetype
        self.position = position
        
        # Load All chess pieces into PIECES
        # K Q B N R
        # k q b n r
        #rescales the pieces file into scale
        SPRITE = pygame.transform.smoothscale(pygame.image.load(pieces_file), (int(SQW*6), int(SQW*2)))
        
        PIECES = ['K','Q','B','N','R','P','k','q','b','n','r','p']
        for i in range(2):
            for j in range(6):
                if piecetype == PIECES[j + i*6]:
                    SURF = pygame.Surface.subsurface(SPRITE, (j*SQW, i*SQW, SQW, SQW))
                    self.image = SURF
        
        self.rect = self.image.get_rect()
        self.rect.x = 100 + (position % 8) * SQW
        self.rect.y = 100 + (position // 8) * SQW

def mouse_pos_to_square(mp):
    """
    Takes a mouse position and translates it into a square number in game from 0-63
    """
    x , y = mp
    if x >= 100 and x <= 100 + SQW*8 and y >= 100 and y <= 100 + SQW*8:
        return ((y-100) // SQW * 8 + (x-100) // SQW)

    
def draw_chess_board_on_screen(game_screen,bg_color,white_square_color,dark_square_color,possible_moves_list):
    game_screen.fill(bg_color)
    pygame.draw.rect(game_screen,dark_square_color,(100,100,600,600))
    #Draw the chess board
    for i in range(0,8):
        for j in range(0,8):
            if i+j*8 in possible_moves_list:
                pygame.draw.rect(game_screen,(white_square_color[0],50,50),(100+SQW*i,100+SQW*j,SQW,SQW))
            elif (i+j) % 2 == 0:
                pygame.draw.rect(game_screen,white_square_color,(100+SQW*i,100+SQW*j,SQW,SQW))

        
def main():
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    DARK = (119,149,86)
    LIGHT = (235,236,208)
    mouse_pos = 0
    possible_moves = []

    pygame.init()

    screen = pygame.display.set_mode((1200,800))
    draw_chess_board_on_screen(screen,WHITE,LIGHT,DARK,possible_moves)
    
    # This is a list of every sprite including the mouse spirite
    all_sprites_list = pygame.sprite.Group()
    
    pygame.font.init() # you have to call this at the start, if you want to use this module.
    myfont = pygame.font.SysFont('Comic Sans MS', 20)
    
    Rematch = True
    
    (all_sprites_list,current_board,current_enpassant,current_turn,current_castle)  = setup_board(starting_board)
    pygame.display.update(all_sprites_list.draw(screen))

    
    while Rematch:
        pygame.display.flip()


        

        for event in pygame.event.get():
            if (event.type == pygame.QUIT) | (pygame.key.get_pressed()[K_ESCAPE]):
                Rematch = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #event.type == 5: #mouse left button down (1: Left-click , 2= Middle-click , 3=Right-click)
                textsurface = myfont.render('Mouse Position: {}'.format(mouse_pos), False, WHITE) #draw white to fill the last text with white
                textsurface2 = myfont.render('Possible Moves: {}'.format(possible_moves), False, WHITE) #draw white to fill the last text with white
                pygame.display.update(screen.blit(textsurface,(700,400))) #draw white to fill the last text with white
                pygame.display.update(screen.blit(textsurface2,(700,440))) #draw white to fill the last text with white
                
                mouse_pos = mouse_pos_to_square(pygame.mouse.get_pos())
                possible_moves = get_possible_moves(mouse_pos,current_board,en_passant=current_enpassant)[0]

                draw_chess_board_on_screen(screen,WHITE,LIGHT,DARK,possible_moves) #Draw the board
                pygame.display.update(all_sprites_list.draw(screen)) #draw all the pieces
                
                textsurface = myfont.render('Mouse Position: {}'.format(mouse_pos), False, BLACK)
                textsurface2 = myfont.render('Possible Moves: {}'.format(possible_moves), False, BLACK)
                pygame.display.update(screen.blit(textsurface,(700,400)))
                pygame.display.update(screen.blit(textsurface2,(700,440)))
                
   
    #Exit pygame incase Escape is pressed or pragram stopped
    pygame.quit()

    
main()
