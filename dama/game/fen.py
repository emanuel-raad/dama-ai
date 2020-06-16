from typing import List

import numpy as np
from numba import njit

from dama.game.move import MoveNode, MoveTypes
from dama.game.bitboard import Bitboard, index, get_row_col, get_empty_board, numpyboard2bitboard, is_piece_present

rowStr = 'abcdefgh'
colStr = '12345678'

def bitboard2fen(bitboard):
    # Reverse the string so that the index of the str is equal to the bitboard square
    boardStr = (bin(bitboard.board)[2:].zfill(64))[::-1]
    
    row = ''
    fenStr = ''
    rowList = []
    counter = 0

    for i in range(0, len(boardStr)):        
        if boardStr[i] == '0':
            counter += 1
        else:
            if counter > 0:
                row += str(counter)
                counter = 0

            if is_piece_present(i, bitboard.myPawn):
                row += 'P'
            elif is_piece_present(i, bitboard.myKing):
                row += 'Q'
            elif is_piece_present(i, bitboard.oppPawn):
                row += 'p'
            elif is_piece_present(i, bitboard.oppKing):
                row += 'q'

        if (i+1) % 8 == 0:
            if counter > 0:
                row += str(counter)
                counter = 0

            rowList.append(row)
            row = ''

    for i in reversed(range(0, 8)):
        fenStr += rowList[i]
        if i != 0:
            fenStr += '/'

    return fenStr

def fen2bitboard(fen:str):
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

    npBoard = np.zeros(shape=(8,8))
    for i, row in enumerate(newFen.split('/')):
        for j, col in enumerate(row):
            npBoard[i][j] = int(col)

    myPawn, myKing, oppPawn, oppKing = numpyboard2bitboard(npBoard)

    return Bitboard(myPawn, myKing, oppPawn, oppKing)

def pos2fen(pos:int):
    row, col = get_row_col(pos)
    return rowStr[row] + colStr[row]

def fen2pos(fen:str):
    row = rowStr.find(fen[0])
    col = colStr.find(fen[1])
    return index(row, col)

def movelist2fen(movelist:List[MoveNode]):
    pass
# return fen str