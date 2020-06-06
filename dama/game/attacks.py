import os
import pickle

import numpy as np

from bitOperations import *
from bitboard import *

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

def load_lookup(filePath, fallbackGenerator):
    if os.path.exists(filePath):
        return pickle.load(open(filePath, "rb"))
    else:
        return fallbackGenerator()

def _generate_king_masks(pos):
    row, col = get_row_col(pos)
    masks = (rowMask[row] | colMask[col]) & ~single(row, 0) & ~single(row, 7) & ~single(0, col) & ~single(7, col) & ~single(row, col)
    return masks

def _generate_blockers_mask():
    blockerMasks = np.zeros(64, dtype=np.uint64)
    for i in range(0, 64):
        blockerMasks[i] = _generate_king_masks(i)
    return blockerMasks

def _generate_single_blocker(index, pos, mask):
    blocker = np.uint64(0)
    index = (bin(index)[2:]).zfill(_rookIndexBits[pos])

    for i in range(0, popCount(mask)):
        lsb = bitScanForward(mask)
        mask = mask & ~single(lsb)
        row, col = get_row_col(lsb)

        value = np.uint64(index[i])
        blocker = set_cell_value(blocker, row, col, value)

    return blocker

def _generate_all_blockers():
    allBlockers = np.zeros(shape=(64, 4096), dtype=np.uint64)

    for i in range(0, 64):
        n = np.power(np.uint64(2), _rookIndexBits[i])
        for j in range(0, n):
            allBlockers[i][j] = _generate_single_blocker(j, i, blockerMasks[i])

    return allBlockers

# Calculate the keys and attack results for each board
def _generate_king_lookup():
    kingMagicLookup = np.zeros(shape=(64, 4096), dtype=np.uint64)

    for i in range(0, 64):
        n = np.power(np.uint64(2), _rookIndexBits[i])

        for j in range(0, n):
            blockers = allBlockers[i][j]
            key = (blockers * _rookMagics[i]) >> (np.uint64(64) - _rookIndexBits[i])
            kingMagicLookup[i][key] = HAndVMoves(i, blockers)

    return kingMagicLookup

# I can save this to a file for reusability, but it doesnt take
# that long to compute
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

# Finally, get the attack with this function
def get_king_attack(pos:int, board:int) -> int:
    board &= blockerMasks[pos]
    key = (board * _rookMagics[pos]) >> (np.uint64(64) - _rookIndexBits[pos])
    return kingMagicLookup[pos][key]

def HAndVMoves(s:int, board:int) -> int:
    binaryS = np.uint64(1) << np.uint64(s)
    row, col = get_row_col(s)
    
    possibilitiesHorizontal = (board - (np.uint64(2) * binaryS)) ^ reverse64(reverse64(board) - (np.uint64(2) * reverse64(binaryS)))
    possibilitiesVertical = ((board&colMask[col]) - (np.uint64(2) * binaryS)) ^ reverse64(reverse64(board&colMask[col]) - (np.uint64(2) * reverse64(binaryS)))

    return (possibilitiesHorizontal&rowMask[row]) | (possibilitiesVertical&colMask[col])

# Should be in this order, because the later generators depend on the earlier ones
base = os.path.join(os.path.dirname(__file__), 'lookup')
blockerMasks    = load_lookup(os.path.join(base, "blockers_mask.pkl")    , _generate_blockers_mask)
allBlockers     = load_lookup(os.path.join(base, "all_blocker.pkl")      , _generate_all_blockers)
kingMagicLookup = load_lookup(os.path.join(base, "king_magic_lookup.pkl"), _generate_king_lookup)
pawnSingleMasks = load_lookup(os.path.join(base, "pawn_single.pkl")      , _generate_pawn_single_moves)
pawnDoubleMasks = load_lookup(os.path.join(base, "pawn_double.pkl")      , _generate_pawn_jumps)


if __name__ == '__main__':
    print_bitboard([ get_king_attack(get_rand_king_index(), get_rand_board()) ])