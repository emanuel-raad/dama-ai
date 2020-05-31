import numpy as np

from dataclasses import dataclass
from dama.game.constants import Color


@dataclass
class Piece:
    '''Class to represent a piece'''
    position : np.ndarray
    promoted : bool
    owner :  Color