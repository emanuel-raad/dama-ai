import numpy as np
from treelib import Node, Tree

from dama.game.dama import DamaGame
from dama.agents.placeholder import getPlaceholder
from dama.game.constants import Color
from dama.game.gameboard import Gameboard

'''
Some functions that will help the agent
classes make trees of the possible
evaluations.
'''

class State(object):
    '''
    Class to store the representation of the game at each
    node of the tree.
    '''
    def __init__(self, gameboard, move, remove):
        self.gameboard = gameboard
        self.move = move
        self.remove = remove

def getMoveTree(
    parentBoard, moveList, removeList, color, depth,
    tree = None, parentNode = None, game = None
    ):

    if tree is None:
        tree = Tree()
        state = State(parentBoard, None, None)
        parentNode = Node(data=state)
        tree.add_node(parentNode)

    if game is None:
        game = DamaGame(board=parentBoard)

    for move, remove in zip(moveList, removeList):

        childBoard = Gameboard(gameboard=np.copy(parentBoard.gameboard))

        game.performMove(
            move, remove, temp_gameboard=childBoard
        )
        
        state = State(childBoard, move, remove)
        node = Node(data=state)
        tree.add_node(node, parent=parentNode)

        player = getPlaceholder(color, opposite=True)

        res = game.get_all_legal_moves(player, temp_gameboard=childBoard)

        if depth is not 0:
            getMoveTree(
                childBoard, res['move'], res['remove'], player.color, depth - 1,
                tree, node
            )

    return tree