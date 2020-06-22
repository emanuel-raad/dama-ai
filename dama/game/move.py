from enum import Enum
from typing import List

import numpy as np
from dama.game.constants import Color, Pieces

class MoveTypes(Enum):
    QUIET = 'Quiet'
    JUMP = 'Jump'
    START = 'Start'

class MoveNode(object):
    """Class to represent a move
    """
    def __init__(self, moveFrom, moveTo=None, capture=None, moveType=None, promotion=False, gameboard=None):
        """Initialize a move

        Args:
            moveFrom (np.uint64, optional): Starting position, indexed from 0-63. Defaults to None.
            moveTo (np.uint64, optional): End position, indexed from 0-63. Defaults to None.
            capture (np.uint64, optional): Enemy square being captured, indexed from 0-63. Defaults to None.
            moveType (MoveTypes, optional): Indicates whether move is jump or quiet. Defaults to None.
            promotion (bool, optional): True if piece get promoted at moveTo location. Defaults to False.
        """
        self.moveFrom  = moveFrom
        self.moveTo    = moveTo
        self.capture   = capture
        self.moveType  = moveType
        self.promotion = promotion
        self.gameboard = gameboard

        # self.tag = "(From:{} To:{} Capture:{})".format(self.moveFrom, self.moveTo, self.capture)
        self.tag = "(F:{} T:{} C:{})".format(self.moveFrom, self.moveTo, self.capture)

    def is_empty(self):
        return self.moveTo is None and self.capture is None
