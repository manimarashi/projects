#inspired by : https://www.youtube.com/watch?v=U4ogK0MIzqk&ab_channel=SebastianLague

import pygame, sys, random, time, json
import numpy as np
from pygame.locals import *

pieces_file = './Files/Pieces.png' #file with image of pieces
SQW = 75 #Square width
RANKS = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
SCORES = {'K':40000,'k':-40000,'Q':900,'q':-900,'R':500,'r':-500,'B':300,'b':-300,'N':300,'n':-300,'P':100,'p':-100}
#FEN Notation: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
starting_board = 'r3k2r/pbp1q1pp/1pn1pb1n/3p1p2/3P1P2/1PN1PN2/PQPBB1PP/R3K2R w KQkq - 0 1'
# Standard Game: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
# Random Board: 'r2q1rk1/pp2ppbp/5np1/1Ppp2B1/3PP1b1/Q1P2N2/P4PPP/3RKB1R b K c6 0 13'
# Castling Test: 'r3k2r/pbp1q1pp/1pn1pb1n/3p1p2/3P1P2/1PN1PN2/PQPBB1PP/R3K2R w KQkq - 0 1'

def play_sound(sound):
    pygame.mixer.init()
    sound_effect_start = pygame.mixer.Sound ('./Files/start.wav')
    sound_effect_move = pygame.mixer.Sound ('./Files/move.wav')
    sound_effect_castle = pygame.mixer.Sound ('./Files/castle.wav')
    sound_effect_take = pygame.mixer.Sound ('./Files/take.wav')
    sound_effect_check = pygame.mixer.Sound ('./Files/check.wav')
    sound_effect_gameover = pygame.mixer.Sound ('./Files/gameover.wav')

    if sound == 'start':
        sound_effect_start.play()
    elif sound == 'move':
        sound_effect_move.play()
    elif sound == 'castle':
        sound_effect_castle.play()
    elif sound == 'take':
        sound_effect_take.play()
    elif sound == 'check':
        sound_effect_check.play()
    elif sound == 'gameover':
        sound_effect_gameover.play()


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
    
    if position == None or position == []:
        return([],[])
    
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
            #can't move two squares if at the rank before last rank
            if i==1 and (board[position]=='p' and y==6 or board[position]=='P' and y==1):
                break
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
        #castling the king
        if possible_castles and possible_castles != '-' and possible_castles != '':
            if possible_castles.find('K') >= 0 and board[position]=='K' and board[61]==None and board[62]==None and set({60,61,62}).isdisjoint(controlled_area(board,'b')):
                possible_moves.append(62)
            if possible_castles.find('Q') >= 0 and board[position]=='K' and board[59]==None and board[58]==None and set({58,59,60}).isdisjoint(controlled_area(board,'b')):
                possible_moves.append(58)
            if possible_castles.find('k') >= 0 and board[position]=='k' and board[5]==None and board[6]==None and set({4,5,6}).isdisjoint(controlled_area(board,'w')):
                possible_moves.append(6)                
            if possible_castles.find('q') >= 0 and board[position]=='k' and board[3]==None and board[2]==None and set({4,3,2}).isdisjoint(controlled_area(board,'w')):
                possible_moves.append(2)                     
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
    def update(self,piecetype,position):
        """ updatin piece location and type, basically same as the init method"""
        self.piecetype = piecetype
        self.position = position
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
    def taken(self):
        self.position = 99
        self.rect = self.image.get_rect()
        if self.piecetype.isupper() == True:
            self.rect.x = 750
            self.rect.y = 600
        else:
            self.rect.x = 750
            self.rect.y = 100

def mouse_pos_to_square(mp):
    """
    Takes a mouse position and translates it into a square number in game from 0-63
    """
    x , y = mp
    if x >= 100 and x <= 100 + SQW*8 and y >= 100 and y <= 100 + SQW*8:
        return ((y-100) // SQW * 8 + (x-100) // SQW)
    else:
        return([])

    
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

def move_piece(board,from_position,to_position,possible_castles):
    enpassantposition = [] #gets populated when a pawn jumps two squares
    spirit_updates = {}
    castlesused = ''
    sound_effect = ''
    #moving pawns
    if board[from_position] in ['p','P']:
        #if a pawn jumps two pieces
        if abs(from_position-to_position)==16:
            if from_position>to_position: #if it is white pawn that is jumping two pieces
                enpassantposition = from_position - 8
            else: #white pawn that is jumping two pieces
                enpassantposition = from_position + 8
            
            spirit_updates = {from_position:{to_position:board[from_position]}} #captures updates that needs to happen for spirits
            board[to_position] = board[from_position]
            board[from_position] = None
            sound_effect = 'move'
        elif abs(to_position - from_position) in [7,9]: #pawn taking another piece either directly or by en passant
            if board[to_position] != None:
                spirit_updates = {to_position:None,from_position:{to_position:board[from_position]}} #captures updates that needs to happen for spirits
                board[to_position] = board[from_position]
                board[from_position] = None
                
            else: # en passant
                if to_position - from_position in [-7,9]:
                    spirit_updates = {from_position + 1: None,from_position:{to_position:board[from_position]}} #captures updates that needs to happen for spirits
                    board[from_position + 1] = None
                elif to_position - from_position in [-9,7]:
                    spirit_updates = {from_position - 1: None,from_position:{to_position:board[from_position]}} #captures updates that needs to happen for spirits
                    board[from_position - 1] = None
                
                board[to_position] = board[from_position]
                board[from_position] = None
            sound_effect = 'take'
            
        else: # regular pawn poves
            spirit_updates = {from_position:{to_position:board[from_position]}}
            board[to_position] = board[from_position]
            board[from_position] = None  
            sound_effect = 'move'

        #promotion of a pawn to queen! for now only promotes to queen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if to_position <= 7: #if a white pawn gets to the 8th rank
            spirit_updates[from_position] = {to_position:'Q'} #captures updates that needs to happen for spirits
            board[to_position] = 'Q'
            board[from_position] = None
        elif to_position >= 56: #if a black pawn gets to the 1st rank
            spirit_updates[from_position]= {to_position:'q'} #captures updates that needs to happen for spirits
            board[to_position] = 'q'
            board[from_position] = None
    #handling king moves and castles
    elif board[from_position] in ['k','K']:
        #both castle options are exhausted at this point since king is moving
        if board[from_position] == 'K':
            castlesused = 'KQ'
        else:
            castlesused = 'kq'
    
        if from_position == 60 and to_position == 62: #white king castles king side
            spirit_updates = {60:{62:'K'},63:{61:'R'}}
            board[62] = 'K'
            board[60] = None
            board[61] = 'R'
            board[63] = None
            sound_effect ='castle'
        elif from_position == 60 and to_position == 58: #white king castles queen side
            spirit_updates = {60:{58:'K'},56:{59:'R'}}
            board[58] = 'K'
            board[60] = None
            board[59] = 'R'
            board[56] = None
            sound_effect ='castle'
        elif from_position == 4 and to_position == 6: #black king castles king side
            spirit_updates = {4:{6:'k'},7:{5:'r'}}
            board[6] = 'k'
            board[4] = None
            board[5] = 'r'
            board[7] = None
            sound_effect ='castle'
        elif from_position == 4 and to_position == 2: #black king castles queen side
            spirit_updates = {4:{2:'k'},0:{3:'r'}}
            board[2] = 'k'
            board[4] = None
            board[3] = 'r'
            board[0] = None
            sound_effect ='castle'
        elif board[to_position] != None: #indicating any king moves that takes a piece
            spirit_updates = {to_position: None,from_position:{to_position:board[from_position]}}
            board[to_position] = board[from_position]
            board[from_position] = None
            sound_effect ='castle'
        else:
            spirit_updates = {from_position:{to_position:board[from_position]}}
            board[to_position] = board[from_position]
            board[from_position] = None
            sound_effect ='castle'
    
    #handling rook moves since it affects castles
    elif board[from_position] in ['r','R']:
        if board[from_position] == 'R' and from_position == 63:
            castlesused = 'K'
        elif board[from_position] == 'R' and from_position == 56:
            castlesused = 'Q'        
        elif board[from_position] == 'r' and from_position == 7:
            castlesused = 'k'
        elif board[from_position] == 'r' and from_position == 0:
            castlesused = 'q'
        
        if board[to_position] != None: #rook takes a piece
            spirit_updates = {to_position: None,from_position:{to_position:board[from_position]}}
            board[to_position] = board[from_position]
            board[from_position] = None
            sound_effect ='take'
        else: #regular rook move
            spirit_updates = {from_position:{to_position:board[from_position]}}
            board[to_position] = board[from_position]
            board[from_position] = None
            sound_effect ='move'
    #taking a piece
    elif board[to_position] != None:
        spirit_updates = {to_position: None,from_position:{to_position:board[from_position]}}
        board[to_position] = board[from_position]
        board[from_position] = None
        sound_effect ='take'
    #all other moves
    else:
        spirit_updates = {from_position:{to_position:board[from_position]}}
        board[to_position] = board[from_position]
        board[from_position] = None
        sound_effect ='move'

        
    #getting which castles were used and removing them from possible castling options
    for character in castlesused:
        possible_castles = possible_castles.replace(character, '')
        
    return(board,enpassantposition,spirit_updates,sound_effect,possible_castles)



def update_spirits(Spirit_group,spirit_update_dict):
    for from_,to_ in spirit_update_dict.items():
        for spirit in Spirit_group:
            if spirit.position == from_:
                if to_ == None:
                    spirit.taken()
                else:
                    to_position = list(to_.keys())[0]
                    spirit.update(to_[to_position],to_position)#getting the piece type str from the spirit_update_dict
                break #no need to go through all other items once a match has been found.
                
    return(Spirit_group)

def evaluate_board(baord_str):
    value = sum(list(map(SCORES.get, baord_str)))
    return(value)





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
    
    # piece_highlighted = False #this is to indicate if a piece is currently highlighted or not

    play_sound('start')
    
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
                
                if mouse_pos in possible_moves:
                    (current_board,current_enpassant,spirit_updates_string,sound_effect,current_castle) = move_piece(current_board,last_mouse_pos,mouse_pos,current_castle)
                    
                    all_sprites_list = update_spirits(all_sprites_list,spirit_updates_string)
                    possible_moves=[]
                    last_mouse_pos=None
                    if current_turn == 'w':
                        current_turn = 'b'
                    else:
                        current_turn = 'w'
                    
                    play_sound(sound_effect)
                    
                elif mouse_pos == []:
                    possible_moves=[]
                elif current_board[mouse_pos] == None:
                    possible_moves=[]
                elif possible_moves==[] and (current_turn == 'w' and current_board[mouse_pos].isupper() == True or current_turn == 'b' and current_board[mouse_pos].isupper() == False):
                    possible_moves = get_possible_moves(mouse_pos,current_board,en_passant=current_enpassant,possible_castles=current_castle)[0] #get the list of possible moves
                    # piece_highlighted = True #get ready to move
                    last_mouse_pos = mouse_pos #record mouse position

                else:
                    possible_moves=[]
                    last_mouse_pos=None

                draw_chess_board_on_screen(screen,WHITE,LIGHT,DARK,possible_moves) #Draw the board
                all_sprites_list.draw(screen) #draw all the pieces
                
                textsurface = myfont.render('Mouse Position: {}'.format(mouse_pos), False, BLACK)
                textsurface2 = myfont.render('Possible Moves: {}'.format(possible_moves), False, BLACK)
                pygame.display.update(screen.blit(textsurface,(700,400)))
                pygame.display.update(screen.blit(textsurface2,(700,440)))
                
    #Exit pygame incase Escape is pressed or pragram stopped
    pygame.quit()

    
main()
