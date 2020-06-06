import numpy as np
from multipledispatch import dispatch
import struct

u64high = np.uint64(0xffffffffffffffff)

rowMask = [None] * 8
rowMask[0] = np.uint64(0b0000000000000000000000000000000000000000000000000000000011111111)
rowMask[1] = np.uint64(0b0000000000000000000000000000000000000000000000001111111100000000)
rowMask[2] = np.uint64(0b0000000000000000000000000000000000000000111111110000000000000000)
rowMask[3] = np.uint64(0b0000000000000000000000000000000011111111000000000000000000000000)
rowMask[4] = np.uint64(0b0000000000000000000000001111111100000000000000000000000000000000)
rowMask[5] = np.uint64(0b0000000000000000111111110000000000000000000000000000000000000000)
rowMask[6] = np.uint64(0b0000000011111111000000000000000000000000000000000000000000000000)
rowMask[7] = np.uint64(0b1111111100000000000000000000000000000000000000000000000000000000)
 
colMask = [None] * 8
colMask[0] = np.uint64(0b0000000100000001000000010000000100000001000000010000000100000001)
colMask[1] = np.uint64(0b0000001000000010000000100000001000000010000000100000001000000010)
colMask[2] = np.uint64(0b0000010000000100000001000000010000000100000001000000010000000100)
colMask[3] = np.uint64(0b0000100000001000000010000000100000001000000010000000100000001000)
colMask[4] = np.uint64(0b0001000000010000000100000001000000010000000100000001000000010000)
colMask[5] = np.uint64(0b0010000000100000001000000010000000100000001000000010000000100000)
colMask[6] = np.uint64(0b0100000001000000010000000100000001000000010000000100000001000000)
colMask[7] = np.uint64(0b1000000010000000100000001000000010000000100000001000000010000000)
 
emptyBoard = np.uint64(0)
row_size = 8

def is_piece_present(board : int, row : int, col : int) -> bool:
    one = np.uint64(1)
    shift = np.uint64((row * row_size + col))
    mask = one << shift
    return ((board & mask) != 0)
 
def set_cell_value(board : int, row : int, col : int, value:int) -> int:
    shift = np.uint64((row * row_size + col))
    newBit = np.uint64(value) << shift
    return (board | newBit)

def initialize_board(rows) -> int:
    board = np.uint64(0)
 
    for i in rows:
        for j in range(0, 8):
            board = set_cell_value(board, i, j, 1)
 
    return board

def array2bit(arr):
    return np.packbits(np.flip(arr, axis=1)).view(np.uint64).byteswap()[0]
 
def bit2array(x):
    return np.flip(np.unpackbits(np.array(list(reversed(struct.pack('Q', x))), dtype=np.uint8).reshape(-1, 1), axis=1), axis=1)
 
def index(row, col):
    return row*8 + col
 
@dispatch(int)
def single(pos):
    return np.uint64(1) << np.uint64(pos)

@dispatch(np.uint64)
def single(pos):
    return np.uint64(1) << pos

@dispatch(int, int)
def single(row, col):
    return np.uint64(1) << np.uint64(index(row, col))

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

def get_row_col(i:int):
    row = int(i / 8)
    col = int(i % 8)
    return (row, col)

def get_rand_board():
    return np.random.randint(0,u64high, dtype=np.uint64)

def get_rand_king():
    return np.uint64(1) << np.random.randint(0,63, dtype=np.uint64)

def get_rand_king_index():
    return np.random.randint(0,63, dtype=np.uint64)

def safe_right(x, shift = np.uint64(1)):
    empty = np.uint64(0)
    one = np.uint64(1)
    eight = np.uint64(8)
    counter = np.uint64(0)
    mask = np.uint64(0xff)
 
    while (x):
        movedRow = ((x & mask) << shift) & mask
        shiftedRow = movedRow << np.uint64(eight*counter)

        empty ^= shiftedRow
        x >>= eight
        counter += one

    return empty

def safe_left(x, shift = np.uint64(1)):
    empty = np.uint64(0)
    one = np.uint64(1)
    eight = np.uint64(8)
    counter = np.uint64(0)
    mask = np.uint64(0xff)
 
    while (x):
        movedRow = ((x & mask) >> shift) & mask
        shiftedRow = movedRow << np.uint64(eight*counter)

        empty ^= shiftedRow
        x >>= eight
        counter += one

    return empty

def safe_up(x, shift=np.uint64(1)):
    return x << (np.uint(8) * shift)

# https://stackoverflow.com/questions/49592295/getting-the-position-of-1-bits-in-a-python-long-object
def get_active_indices(board : int):
    one_bit_indexes = []
    index = 0
    count = 0
    one = np.uint64(1)
    while board: # returns true if sum is non-zero
        if board & one: # returns true if right-most bit is 1
            one_bit_indexes.append(index)
            count += 1
        board >>= one # discard the right-most bit
        index += 1
    return one_bit_indexes
