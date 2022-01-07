import pandas as pd
import numpy as np
#import re
import random, time, json, os
#import matplotlib.pyplot as plt
#from pylab import *

#---------------------------------------- XY posiotion of the pieces --------------------------------------
# piecepositionX = [100, 400, 700, 150, 400, 650, 200, 400, 600, 100, 150, 200, 600, 650, 700, 200, 400, 600, 150, 400, 600, 100, 400, 700]
# piecepositionY = [700, 700, 700, 650, 650, 650, 600, 600, 600, 400, 400, 400, 400, 400, 400, 200, 200, 200, 150, 150, 150, 100, 100, 100]

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

#----------------- check if boards dict exists if not initiate one ---------------
#del boards
starttime = time.time()
for games in range(1000000):
    #reset the board
    boardstr = '------------------------'
    #white always plays first
    turn = 'w'
    #If boards is not initiated initiate it
    try:
        boards
    except NameError:
        boards={boardstr:{}} #'turn':turn
        
    #stores only current board for assigning the rewards at the end of turn
    currentboard = [boardstr]
    while checkboard(boardstr)[0]:
        #select a random cell from available cells
        #cell = random.choice([i for i, ltr in enumerate(boardstr) if ltr == '-'])
        #update table string
        boardstr = AIMove(BoardsDict=boards , Boardstr=boardstr , Turn=turn , RandomMoveChance = 1.8-games/1000000)#boardstr[:cell] + turn + boardstr[cell+1:]
        #change turn flag
        turn = 'b' if turn=='w' else 'w'
        #add to CURRENT BOARD dictionary
        currentboard.append(boardstr)
    
    #Number of moves
    NumberofMoves = len(currentboard)-1
    #Outcome of the game - pulls the first letter only w:white wins, b:black wins or d: draw
    boardstatus = checkboard(boardstr)[1][0]
    #reward function and update main dict
    for i in range(NumberofMoves):
        try: #try to update values
            if ((i%2 == 0) & (boardstatus=='w')) | ((i%2 == 1) & (boardstatus=='b')):
                boards[currentboard[i]][currentboard[i+1]] += 1/NumberofMoves
            elif ((i%2 == 0) & (boardstatus=='b')) | ((i%2 == 1) & (boardstatus=='w')):
                boards[currentboard[i]][currentboard[i+1]] -= 1/NumberofMoves#boards[currentboard[i]][currentboard[i+1]]* 0.99**i
        except KeyError: #error could be due to 2 problems: 1- base table exists but move does not exist 2- Base table does not exist
            try:  #in case the base table exists but the move does not
                if ((i%2 == 0) & (boardstatus=='w')) | ((i%2 == 1) & (boardstatus=='b')):
                    boards[currentboard[i]][currentboard[i+1]] = 1/NumberofMoves
                elif ((i%2 == 0) & (boardstatus=='b')) | ((i%2 == 1) & (boardstatus=='w')):
                    boards[currentboard[i]][currentboard[i+1]] = 0
            except KeyError: #in case even the base table does not exist
                boards[currentboard[i]] = {} #Add base table to the boards dict to be able to define a move
                if ((i%2 == 0) & (boardstatus=='w')) | ((i%2 == 1) & (boardstatus=='b')):
                    boards[currentboard[i]][currentboard[i+1]] = 1/NumberofMoves
                elif ((i%2 == 0) & (boardstatus=='b')) | ((i%2 == 1) & (boardstatus=='w')):
                    boards[currentboard[i]][currentboard[i+1]] = 0

    #print final result
    #checkboard(boardstr)[1]
hours, rem = divmod(time.time() - starttime, 3600)
minutes, seconds = divmod(rem, 60)
print( 'Learning Time: {:0>2}:{:0>2}:{:04.1f}'.format(int(hours),int(minutes),seconds))

#Save the file as json to read later
starttime = time.time()
with open('./RLGameMoves.json', 'w') as f:
    json.dump(boards, f)

hours, rem = divmod(time.time() - starttime, 3600)
minutes, seconds = divmod(rem, 60)
print( 'Saving json file time: {:0>2}:{:0>2}:{:04.1f}'.format(int(hours),int(minutes),seconds))
print('File Size: %.f MB' % (os.stat('./RLGameMoves.json').st_size/1000000) )
