   
import numpy as np

from dama.game.constants import Color
from dama.game.gameboard import Gameboard

from dama.game.move import Move
from treelib import Node, Tree

class Rules:

    @staticmethod
    def generate_potential_moves():
        '''
        Need to generate a tree where each edge is the move performed
        and each node is the board?
        Do this with do/undo instead of copying the gameboard each time
        Try to do iteratively as wells
        '''
        
        moveTree = Tree()

        return moveTree

    @staticmethod
    def is_valid_slide(gameboard : Gameboard, color : Color, startPosition, endPosition) -> bool:
        '''
        Maybe instead I should generate all the possible moves and then
        prune the invalid ones. That way I won't get weird inputs like
        diagonal movements or moving more than one square
        '''
        
        isPromoted = gameboard.is_promoted(startPosition)
        dist = abs(np.linalg.norm(endPosition - startPosition))

        # Out of board
        if gameboard.is_outside_board(endPosition):
            return False

        # End position occupied
        elif not gameboard.is_empty(endPosition):
            return False

        # Trying to move more than 1 unit
        elif dist > 1 and not isPromoted:
            return False

        return True

    @staticmethod
    def is_valid_jump(gameboard : Gameboard, color : Color, startPosition, endPosition) -> bool:
        return True