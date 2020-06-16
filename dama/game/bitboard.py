import struct
from dataclasses import dataclass
from random import randint

import numba as nb
import numpy as np
from multipledispatch import dispatch
from numba import int64, jit, njit, uint64

from dama.game.bitOperations import clear_bit, set_bit, toggle_bit, reverse64
from dama.game.move import MoveNode, MoveTypes

u64high = 0xffffffffffffffff

rowMask = np.array([
    0b0000000000000000000000000000000000000000000000000000000011111111,
    0b0000000000000000000000000000000000000000000000001111111100000000,
    0b0000000000000000000000000000000000000000111111110000000000000000,
    0b0000000000000000000000000000000011111111000000000000000000000000,
    0b0000000000000000000000001111111100000000000000000000000000000000,
    0b0000000000000000111111110000000000000000000000000000000000000000,
    0b0000000011111111000000000000000000000000000000000000000000000000,
    0b1111111100000000000000000000000000000000000000000000000000000000
], dtype=np.uint64)

colMask = np.array([
    0b0000000100000001000000010000000100000001000000010000000100000001,
    0b0000001000000010000000100000001000000010000000100000001000000010,
    0b0000010000000100000001000000010000000100000001000000010000000100,
    0b0000100000001000000010000000100000001000000010000000100000001000,
    0b0001000000010000000100000001000000010000000100000001000000010000,
    0b0010000000100000001000000010000000100000001000000010000000100000,
    0b0100000001000000010000000100000001000000010000000100000001000000,
    0b1000000010000000100000001000000010000000100000001000000010000000
], dtype=np.uint64)

@njit(uint64(uint64, uint64), cache=True)
def is_piece_present(pos, board):
    mask = 1 << pos
    return (board & mask) != 0

def initialize_board(rows):
    board = 0
 
    for i in rows:
        for j in range(0, 8):
            board = set_bit(i*8+j, board)
 
    return board

def array2bit(arr):
    return np.packbits(np.flip(arr, axis=1)).view(np.uint64).byteswap()[0]

def bit2array(x):
    return np.flip(np.unpackbits(np.array(list(reversed(struct.pack('Q', x))), dtype=np.uint8).reshape(-1, 1), axis=1), axis=1)

def print_bitboard(bits, pad=8):
    boards = []
    for i in bits:
        boards.append(bit2array(i))
 
    padding = ''
    for i in range(pad):
        padding += ' '
 
    for i in range(8):
        boardStr = ''
        for j in range(len(boards)):
            boardStr += ("{}{}".format(boards[j][i], padding))
        print(boardStr)

def get_rand_board():
    return uint64(randint(0, u64high))

def get_rand_pos():
    return randint(0, 63)

@njit(cache=True)
def index(row, col):
    return row*8 + col

@njit(uint64(uint64), cache=True)
def single(pos):
    return 1 << pos

@njit(nb.typeof((uint64(0), uint64(0)))(uint64), cache=True)
def get_row_col(i):
    row = int(i / 8)
    col = int(i % 8)
    return (row, col)

@njit(uint64(), cache=True)
def get_rand_king():
    return 1 << randint(0,63)

# https://stackoverflow.com/questions/49592295/getting-the-position-of-1-bits-in-a-python-long-object
# @njit(cache=True)
# def get_active_indices(board : int):
#     one_bit_indexes = []
#     index = 0
#     count = 0

#     while board: # returns true if sum is non-zero
#         if board & 1: # returns true if right-most bit is 1
#             one_bit_indexes.append(index)
#             count += 1
#         board >>= 1 # discard the right-most bit
#         index += 1
#     return one_bit_indexes

def get_active_indices(board : int):
    one_bit_indexes = []
    index = 0
    count = 0
    one = np.uint64(1)
    board = np.uint64(board)
    
    while board: # returns true if sum is non-zero
        if board & one: # returns true if right-most bit is 1
            one_bit_indexes.append(index)
            count += 1
        board >>= one # discard the right-most bit
        index += 1
    return one_bit_indexes

@njit(cache=True)
def move_piece(start, end, board):
    board = set_bit(end, board)
    board = clear_bit(start, board)
    return board

@njit(nb.typeof((uint64(0), uint64(0), uint64(0), uint64(0)))(uint64), cache=True)
def generate_ray_masks(x):
    row, col = get_row_col(x)

    north = uint64(0)
    south = uint64(0)
    east = uint64(0)
    west = uint64(0)

    for i in range(1, 8-row):
        north = set_bit(i*8 + x, north)

    for i in range(1, row+1):
        south = set_bit(x - i*8, south)

    for i in range(1, 8-col):
        east = set_bit(x + i, east)

    for i in range(1, col+1):
        west = set_bit(x - i, west)

    return (south, west, east, north)

rayMasks = np.zeros(shape=(64, 4))
rayMasks = [generate_ray_masks(x) for x in range(0, 64)]

def promote(pos, myPawn, myKing):
    myPawn = clear_bit(pos, myPawn)
    myKing = set_bit(pos, myKing)

    return myPawn, myKing

def check_promotions(myPawn):
    masked = np.uint64(myPawn) & rowMask[7]
    if masked != 0:
        indices = get_active_indices(masked)
        if len(indices) > 1 :
            raise MultiplePawnPromote
        else:
            return True, indices[0]
    else:
        return False, 0

class Bitboard():
    def __init__(self, myPawn, myKing, oppPawn, oppKing):
        self.myPawn = myPawn
        self.myKing = myKing
        self.oppPawn = oppPawn
        self.oppKing = oppKing
        self.board = myPawn | myKing | oppPawn | oppKing
        self.oppBoard = oppPawn | oppKing
        self.myBoard = myPawn | myKing

def get_empty_board():
    return Bitboard(np.uint64(0), np.uint64(0), np.uint64(0), np.uint64(0))

def perform_move(moveList, myPawn, myKing, oppPawn, oppKing):
    myBoards = [myPawn, myKing]
    oppBoards = [oppPawn, oppKing]
    
    for move in moveList:
        for i in range(0, len(myBoards)):
            if is_piece_present(move.moveFrom, myBoards[i]):
                myBoards[i] = toggle_bit(move.moveFrom, myBoards[i])
                myBoards[i] = toggle_bit(move.moveTo, myBoards[i])
        if move.capture is not None:
            for i in range(0, len(oppBoards)):
                if is_piece_present(move.capture, oppBoards[i]):
                    oppBoards[i] = toggle_bit(move.capture, oppBoards[i])
        if move.promotion == True:
            myBoards[0], myBoards[1] = promote(move.moveTo, myBoards[0], myBoards[1])
    
    return myBoards[0], myBoards[1], oppBoards[0], oppBoards[1]

def perform_move_board(moveList, board):
    myPawn, myKing, oppPawn, oppKing = perform_move(moveList, board.myPawn, board.myKing, board.oppPawn, board.oppKing)
    return Bitboard(myPawn, myKing, oppPawn, oppKing)

def flip_color(board):
    return Bitboard(
        reverse64(board.oppPawn), reverse64(board.oppKing), reverse64(board.myPawn), reverse64(board.myKing)
    )

def numpyboard2bitboard(board):
    myPawn = np.uint64(0)
    myKing = np.uint64(0)
    oppPawn = np.uint64(0)
    oppKing = np.uint64(0)

    for i in range(0, len(board)):
        for j in range(0, len(board[i])):
            idx = (7-i)*8 + j

            if board[i][j] == 1:
                myPawn = set_bit(idx, myPawn)
            elif board[i][j] == 2:
                myKing = set_bit(idx, myKing)
            elif board[i][j] == 3:
                oppPawn = set_bit(idx, oppPawn)
            elif board[i][j] == 4:
                oppKing = set_bit(idx, oppKing)

    return np.uint64(myPawn), np.uint64(myKing), np.uint64(oppPawn), np.uint64(oppKing)