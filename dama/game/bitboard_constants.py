from dataclasses import dataclass

import numpy as np

from bitboard import array2bit, initialize_board


@dataclass
class BoardParent:
    myPawn   : np.uint64
    myKing   : np.uint64
    oppPawn  : np.uint64
    oppKing  : np.uint64
    board    : np.uint64
    oppBoard : np.uint64


@dataclass
class StartingBoard(BoardParent):
    myPawn = initialize_board([1, 2])
    oppPawn = initialize_board([5, 6])
    myKing = np.uint64(0)
    oppKing = np.uint64(0)

    board = myPawn | myKing | oppPawn | oppKing
    oppBoard = oppPawn | oppKing

@dataclass
class PawnJumps(BoardParent):
    myPawn = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))

    oppPawn = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))

    myKing = np.uint64(0)
    oppKing = np.uint64(0)

    board = myPawn | myKing | oppPawn | oppKing
    oppBoard = oppPawn | oppKing

@dataclass
class KingJumps(BoardParent):
    myPawn = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))

    oppPawn = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))

    myKing = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))
    
    oppKing = np.uint64(0)

    board = myPawn | myKing | oppPawn | oppKing
    oppBoard = oppPawn | oppKing

@dataclass
class KingZigzag(BoardParent):
    myPawn = np.uint64(0)

    myKing = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0]
            ]))
    
    oppKing = np.uint64(0)

    oppPawn = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 1, 1, 0],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 1, 0, 1, 0, 1, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 1, 0, 1, 0, 0]
            ]))

    board = myPawn | myKing | oppPawn | oppKing
    oppBoard = oppPawn | oppKing

@dataclass
class PawnPromote(BoardParent):
    myPawn = array2bit(np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))

    oppPawn = array2bit(np.array([
                [0, 0, 0, 0, 1, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]))

    myKing = np.uint64(0)
    oppKing = np.uint64(0)

    board = myPawn | myKing | oppPawn | oppKing
    oppBoard = oppPawn | oppKing