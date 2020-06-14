import time
from random import randint

import numba as nb
import numpy as np
from numba import jit, njit, uint64

from dama.game.bitOperations import *
from dama.game.bitboard import *

@njit(uint64(uint64, uint64), cache=True)
def rayMoves(pos, board):
    row, col = get_row_col(pos)
    rays = uint64(0)

    # Left
    for i in range(col-1, -1, -1):
        p = index(row, i)
        rays = set_bit(p, rays)
        if is_piece_present(p, board):
            break

    # Right
    for i in range(col+1, 8):
        p = index(row, i)
        rays = set_bit(p, rays)
        if is_piece_present(p, board):
            break

    # Down
    for i in range(row-1, -1, -1):
        p = index(i, col)
        rays = set_bit(p, rays)
        if is_piece_present(p, board):
            break

    # Up
    for i in range(row+1, 8):
        p = index(i, col)
        rays = set_bit(p, rays)
        if is_piece_present(p, board):
            break

    return rays

def _generate_pawn_single_moves():
    moves = []
    for i in reversed(range(0, 8)):
        for j in range(0, 8):
            board = np.zeros(shape=[8,8], dtype=np.uint8)
            if j-1 >= 0:
                board[i][j-1] = 1
            if j+1 <= 7:
                board[i][j+1] = 1
            if i-1 >= 0:
                board[i-1][j] = 1
            moves.append(array2bit(board))
    return moves

def _generate_pawn_jumps():
    moves = []
    for i in reversed(range(0, 8)):
        for j in range(0, 8):
            board = np.zeros(shape=[8,8], dtype=np.uint8)
            if j-2 >= 0:
                board[i][j-2] = 1
            if j+2 <= 7:
                board[i][j+2] = 1
            if i-2 >= 0:
                board[i-2][j] = 1
            moves.append(array2bit(board))    
    return moves

# Magic bitboards
# ~~~~spooky

# A couple constants

_rookMagics = np.array([
    0xa8002c000108020, 0x6c00049b0002001, 0x100200010090040, 0x2480041000800801, 0x280028004000800,
    0x900410008040022, 0x280020001001080, 0x2880002041000080, 0xa000800080400034, 0x4808020004000,
    0x2290802004801000, 0x411000d00100020, 0x402800800040080, 0xb000401004208, 0x2409000100040200,
    0x1002100004082, 0x22878001e24000, 0x1090810021004010, 0x801030040200012, 0x500808008001000,
    0xa08018014000880, 0x8000808004000200, 0x201008080010200, 0x801020000441091, 0x800080204005,
    0x1040200040100048, 0x120200402082, 0xd14880480100080, 0x12040280080080, 0x100040080020080,
    0x9020010080800200, 0x813241200148449, 0x491604001800080, 0x100401000402001, 0x4820010021001040,
    0x400402202000812, 0x209009005000802, 0x810800601800400, 0x4301083214000150, 0x204026458e001401,
    0x40204000808000, 0x8001008040010020, 0x8410820820420010, 0x1003001000090020, 0x804040008008080,
    0x12000810020004, 0x1000100200040208, 0x430000a044020001, 0x280009023410300, 0xe0100040002240,
    0x200100401700, 0x2244100408008080, 0x8000400801980, 0x2000810040200, 0x8010100228810400,
    0x2000009044210200, 0x4080008040102101, 0x40002080411d01, 0x2005524060000901, 0x502001008400422,
    0x489a000810200402, 0x1004400080a13, 0x4000011008020084, 0x26002114058042
], dtype=np.uint64)

_rookIndexBits = np.array([
    12, 11, 11, 11, 11, 11, 11, 12,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12
], dtype=np.uint64)

@njit(uint64(uint64), cache=True)
def _generate_king_masks(pos):
    row, col = get_row_col(pos)
    masks = (rowMask[row] | colMask[col]) \
        & ~single(index(row, 0)) \
        & ~single(index(row, 7)) \
        & ~single(index(0, col)) \
        & ~single(index(7, col)) \
        & ~single(index(row, col))

    return masks

# Then generate all the possible blockers along those masks
def _generate_blockers(idx, pos, mask):
    blocker = np.uint64(0)
    idx = (bin(idx)[2:]).zfill(_rookIndexBits[pos])

    for i in range(0, popCount(mask)):
        lsb = bitScanForward(mask)
        mask = mask & np.uint64(~single(lsb))
        row, col = get_row_col(lsb)
        # think there is something wrong here

        if int(idx[i]) == 1:
            blocker = set_bit(index(row, col), blocker)

    return blocker

def _generate_blockers_mask():
    blockerMasks = np.zeros(64, dtype=np.uint64)
    for i in range(0, 64):
        blockerMasks[i] = _generate_king_masks(i)
        assert popCount(blockerMasks[i]) == _rookIndexBits[i]
    return blockerMasks

def _generate_all_blockers():
    allBlockers = np.zeros(shape=(64, 4096), dtype=np.uint64)
    for i in range(0, 64):
        n = np.power(np.uint64(2), _rookIndexBits[i])
        for j in range(0, n):
            allBlockers[i][j] = _generate_blockers(j, i, blockerMasks[i])
    return allBlockers

def _generate_king_lookup():
    kingMagicLookup = np.zeros(shape=(64, 4096), dtype=np.uint64)
    for i in range(0, 64):
        n = np.power(np.uint64(2), _rookIndexBits[i])

        for j in range(0, n):
            blockers = allBlockers[i][j]
            key = (blockers * _rookMagics[i]) >> (np.uint64(64) - _rookIndexBits[i])
            kingMagicLookup[i][key] = rayMoves(i, blockers)
    return kingMagicLookup

# Finally, get the attack with this function
@njit(cache=True)
def get_king_attack(pos, board, mask, lookup):
    board &= mask[pos]
    key = (board * _rookMagics[pos]) >> (np.uint64(64) - _rookIndexBits[pos])
    return lookup[pos][key]

import pickle
import os
import logging
# pickle.dump(   blockerMasks, open(    "blockers_mask.pkl", "wb"))
# pickle.dump(    allBlockers, open(      "all_blocker.pkl", "wb"))
# pickle.dump(kingMagicLookup, open("king_magic_lookup.pkl", "wb"))

def load_lookup(filePath, fallbackGenerator):
    if os.path.exists(filePath):
        return pickle.load(open(filePath, "rb"))
    else:
        return fallbackGenerator()


#######################################################
# LOAD GLOBAL CONSTANTS

time1 = time.time()
base = os.path.join(os.path.dirname(__file__), 'lookup')
blockerMasks    = load_lookup(os.path.join(base, "blockers_mask.pkl")    , _generate_blockers_mask)
allBlockers     = load_lookup(os.path.join(base, "all_blocker.pkl")      , _generate_all_blockers)
kingMagicLookup = load_lookup(os.path.join(base, "king_magic_lookup.pkl"), _generate_king_lookup)
pawnSingleMasks = load_lookup(os.path.join(base, "pawn_single.pkl")      , _generate_pawn_single_moves)
pawnDoubleMasks = load_lookup(os.path.join(base, "pawn_double.pkl")      , _generate_pawn_jumps)
time2 = time.time()
msg = "Loaded globals in {:.2f} ms".format(1000*(time2-time1))
# print(msg)