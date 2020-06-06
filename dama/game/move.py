import numpy as np

from dataclasses import dataclass
from typing import List

from dama.game.constants import Color
from dama.game.constants import Pieces

@dataclass
class Move:
    '''Class to represent a move'''
        
    # This is an array of positions
    moveTo : List[np.ndarray]

    # This is a list of position in order of capture
    capturedPositions : List[np.ndarray]
    
    # This is a list of dama.game.constants.Piece
    capturedTypes : List[Pieces]

    # The player whose turn it is
    activeColor : Color