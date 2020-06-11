import pickle
import struct
import time
import warnings
from random import randint

import numba as nb
import numpy as np
from numba import jit, njit, uint64

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

emptyBoard = 0

BitReverseTable256 = [
  0x00, 0x80, 0x40, 0xC0, 0x20, 0xA0, 0x60, 0xE0, 0x10, 0x90, 0x50, 0xD0, 0x30, 0xB0, 0x70, 0xF0, 
  0x08, 0x88, 0x48, 0xC8, 0x28, 0xA8, 0x68, 0xE8, 0x18, 0x98, 0x58, 0xD8, 0x38, 0xB8, 0x78, 0xF8, 
  0x04, 0x84, 0x44, 0xC4, 0x24, 0xA4, 0x64, 0xE4, 0x14, 0x94, 0x54, 0xD4, 0x34, 0xB4, 0x74, 0xF4, 
  0x0C, 0x8C, 0x4C, 0xCC, 0x2C, 0xAC, 0x6C, 0xEC, 0x1C, 0x9C, 0x5C, 0xDC, 0x3C, 0xBC, 0x7C, 0xFC, 
  0x02, 0x82, 0x42, 0xC2, 0x22, 0xA2, 0x62, 0xE2, 0x12, 0x92, 0x52, 0xD2, 0x32, 0xB2, 0x72, 0xF2, 
  0x0A, 0x8A, 0x4A, 0xCA, 0x2A, 0xAA, 0x6A, 0xEA, 0x1A, 0x9A, 0x5A, 0xDA, 0x3A, 0xBA, 0x7A, 0xFA,
  0x06, 0x86, 0x46, 0xC6, 0x26, 0xA6, 0x66, 0xE6, 0x16, 0x96, 0x56, 0xD6, 0x36, 0xB6, 0x76, 0xF6, 
  0x0E, 0x8E, 0x4E, 0xCE, 0x2E, 0xAE, 0x6E, 0xEE, 0x1E, 0x9E, 0x5E, 0xDE, 0x3E, 0xBE, 0x7E, 0xFE,
  0x01, 0x81, 0x41, 0xC1, 0x21, 0xA1, 0x61, 0xE1, 0x11, 0x91, 0x51, 0xD1, 0x31, 0xB1, 0x71, 0xF1,
  0x09, 0x89, 0x49, 0xC9, 0x29, 0xA9, 0x69, 0xE9, 0x19, 0x99, 0x59, 0xD9, 0x39, 0xB9, 0x79, 0xF9, 
  0x05, 0x85, 0x45, 0xC5, 0x25, 0xA5, 0x65, 0xE5, 0x15, 0x95, 0x55, 0xD5, 0x35, 0xB5, 0x75, 0xF5,
  0x0D, 0x8D, 0x4D, 0xCD, 0x2D, 0xAD, 0x6D, 0xED, 0x1D, 0x9D, 0x5D, 0xDD, 0x3D, 0xBD, 0x7D, 0xFD,
  0x03, 0x83, 0x43, 0xC3, 0x23, 0xA3, 0x63, 0xE3, 0x13, 0x93, 0x53, 0xD3, 0x33, 0xB3, 0x73, 0xF3, 
  0x0B, 0x8B, 0x4B, 0xCB, 0x2B, 0xAB, 0x6B, 0xEB, 0x1B, 0x9B, 0x5B, 0xDB, 0x3B, 0xBB, 0x7B, 0xFB,
  0x07, 0x87, 0x47, 0xC7, 0x27, 0xA7, 0x67, 0xE7, 0x17, 0x97, 0x57, 0xD7, 0x37, 0xB7, 0x77, 0xF7, 
  0x0F, 0x8F, 0x4F, 0xCF, 0x2F, 0xAF, 0x6F, 0xEF, 0x1F, 0x9F, 0x5F, 0xDF, 0x3F, 0xBF, 0x7F, 0xFF
]

# Flip about horizontal axis
@njit(uint64(uint64))
def flipH(x : int) -> int:
    k1 = 0x00FF00FF00FF00FF
    k2 = 0x0000FFFF0000FFFF
    x = ( (x >>  8)  & k1) | ( (x & k1) <<  8 )
    x = ( (x >> 16) & k2 ) | ( (x & k2) << 16 )
    x = (  x >> 32       ) | (  x       << 32 )
 
    return x

# Flip about vertical axis
@njit(uint64(uint64))
def flipV(x : int) -> int:
    k1 = 0x5555555555555555
    k2 = 0x3333333333333333
    k4 = 0x0F0F0F0F0F0F0F0F
 
    x = ( (x >> 1) & k1 ) | ( (x & k1) << 1 )
    x = ( (x >> 2) & k2 ) | ( (x & k2) << 2 )
    x = ( (x >> 4) & k4 ) | ( (x & k4) << 4 )
 
    return x

@njit(uint64(uint64))
def reverse64(x):
    return flipV(flipH(x))

@njit
def initpopCountOfByte256():
    popCountOfByte256 = np.zeros(256, dtype=np.uint64)
    for i in range(1, 256):
        popCountOfByte256[i] = popCountOfByte256[int(i / 2)] + (i & 1);
    return popCountOfByte256

popMask = np.uint64(0xff)
popCountOfByte256 = initpopCountOfByte256()

@njit(uint64(uint64))
def popCount (x):
   return popCountOfByte256[ x                   & popMask] + \
          popCountOfByte256[(x >>  8) & popMask] + \
          popCountOfByte256[(x >> 16) & popMask] + \
          popCountOfByte256[(x >> 24) & popMask] + \
          popCountOfByte256[(x >> 32) & popMask] + \
          popCountOfByte256[(x >> 40) & popMask] + \
          popCountOfByte256[(x >> 48) & popMask] + \
          popCountOfByte256[ x >> 56]


index64 = np.array([
    0, 47,  1, 56, 48, 27,  2, 60,
   57, 49, 41, 37, 28, 16,  3, 61,
   54, 58, 35, 52, 50, 42, 21, 44,
   38, 32, 29, 23, 17, 11,  4, 62,
   46, 55, 26, 59, 40, 36, 15, 53,
   34, 51, 20, 43, 31, 22, 10, 45,
   25, 39, 14, 33, 19, 30,  9, 24,
   13, 18,  8, 12,  7,  6,  5, 63
])
debruijn64 = np.uint64(0x03f79d71b4cb0a89)

# /**
#  * bitScanReverse
#  * @authors Kim Walisch, Mark Dickinson
#  * @param bb bitboard to scan
#  * @precondition bb != 0
#  * @return index (0..63) of most significant one bit
#  */
# https://www.chessprogramming.org/BitScan#De_Bruijn_Multiplication_2

@njit(uint64(uint64))
def bitScanReverse(bb):
    if bb == 0:
        return 0

    bb |= bb >> np.uint64(1)
    bb |= bb >> np.uint64(2)
    bb |= bb >> np.uint64(4)
    bb |= bb >> np.uint64(8)
    bb |= bb >> np.uint64(16)
    bb |= bb >> np.uint64(32)

    return index64[(bb * debruijn64) >> np.uint64(58)]

# /**
#  * bitScanForward
#  * @author Kim Walisch (2012)
#  * @param bb bitboard to scan
#  * @precondition bb != 0
#  * @return index (0..63) of least significant one bit
#  */
@njit(uint64(uint64))
def bitScanForward(bb):
   if bb == 0:
       return 0
   return index64[((bb ^ (bb-np.uint64(1))) * debruijn64) >> np.uint64(58)]

@njit(uint64(uint64, uint64))
def set_bit(n, bit):
    return bit | (1 << n)

@njit(uint64(uint64, uint64))
def clear_bit(n, bit):
    return bit & (~(1 << n))

@njit(uint64(uint64, uint64))
def toggle_bit(n, bit):
    return bit ^ (1 << n)