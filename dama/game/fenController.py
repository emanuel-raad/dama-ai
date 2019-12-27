import numpy as np
from dama.game.constants import Pieces

def fen2pos(fen):
    # row = 'abcdefgh'
    row = 'abcdefgh'

    x = int(row.find(fen[0]))
    y = int(fen[1])

    return np.array([x, y])

def fen2moves(fen):
    moveList = []

    for i in fen.split('-'):
        moveList.append(fen2pos(i))

    return moveList

def fen2board(fen):
    newFen = ''
    for i in fen:
        if i.isnumeric():
            newFen += '0' * int(i)
        else:
            # UPERCASE white
            # lowercase black
            if   i == 'P' : newFen += '1'
            elif i == 'p' : newFen += '3'
            elif i == 'Q' : newFen += '2'
            elif i == 'q' : newFen += '4'
            elif i == '/' : newFen += i

    board = np.zeros(shape=(8,8))
    for i, row in enumerate(newFen.split('/')):
        for j, col in enumerate(row):
            board[i][j] = int(col)

    return board

def board2fen(board):        
    fen = ''

    for row in board:
        counter = 0
        for j in row:
            if   j == 0 :
                counter += 1
            else:
                if counter > 0:
                    fen += str(counter)
                    counter = 0
                
                # UPERCASE white
                # lowercase black
                if   j == Pieces.WHITE          : fen += 'P'
                elif j == Pieces.WHITE_PROMOTED : fen += 'Q'
                elif j == Pieces.BLACK          : fen += 'p'
                elif j == Pieces.BLACK_PROMOTED : fen += 'q'
            
        if counter > 0:
            fen += str(counter)
            counter = 0
        fen += '/'

    fen = fen[:-1]
    
    return fen

def pos2fen(pos):
    row = 'abcdefgh'
    col = '87654321'

    return row[pos[1]] + col[pos[0]]

def moves2fen(moves):
    fenList = []

    for i in moves:
        fenStr = ''
        for j in i:
            if j is not None:
                fenStr += pos2fen(j)
                fenStr += '-'
        fenStr = fenStr[:-1]
        fenList.append(fenStr)

    return fenList

if __name__ == '__main__':
    # print(fen2moves('a1-a2-a3-b3-b4-b5'))
    # print(fen2board('8/1p1p1p1p/8/8/8/8/8/QQQQQQQQ'))
    
    arr = [np.array([5, 6]), np.array([4, 6])]