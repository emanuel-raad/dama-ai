from enum import IntEnum, Enum

class Pieces(IntEnum):
    EMPTY = 0
    WHITE = 1
    WHITE_PROMOTED = 2
    BLACK = 3
    BLACK_PROMOTED = 4

class Color(Enum):
    WHITE = 1
    BLACK = 2