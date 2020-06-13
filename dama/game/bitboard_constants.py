import numpy as np

from dama.game.bitboard import array2bit, initialize_board, numpyboard2bitboard
import numba as nb

class BoardParent:
    def __init__(self, npBoard, tag=''):
        self.tag = tag
        self.myPawn, self.myKing, self.oppPawn, self.oppKing = numpyboard2bitboard(npBoard)

        self.myBoard = self.myPawn | self.myKing
        self.oppBoard = self.oppPawn | self.oppKing
        self.board = self.myBoard | self.oppBoard

StartingBoard = BoardParent(
    np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [3, 3, 3, 3, 3, 3, 3, 3],
            [3, 3, 3, 3, 3, 3, 3, 3],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]    
    ]), 'Starting Board'
)

PawnJumps = BoardParent(
    np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 3, 0, 1, 0, 0],
            [3, 0, 0, 0, 3, 0, 0, 0],
            [1, 3, 0, 3, 0, 3, 0, 3],
            [3, 0, 0, 0, 3, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]    
    ]), 'Pawn Jumps'
)

KingJumps = BoardParent(
    np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 2, 3, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]    
    ]), 'King Jumps'
)

KingZigzag = BoardParent(
    np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 3, 0, 3, 3, 0],
            [3, 0, 0, 0, 0, 0, 0, 3],
            [0, 0, 3, 0, 3, 0, 3, 0],
            [3, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 3, 0, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 3, 0],
            [2, 3, 0, 3, 0, 3, 0, 0]
    ]), 'King Zigzag'
)

PawnPromote = BoardParent(
    np.array([
            [0, 0, 0, 0, 0, 3, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]    
    ]), 'Pawn Promote'
)

HasJumped = BoardParent(
    np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]    
    ]), 'Has Jumped'
)