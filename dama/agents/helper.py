import numpy as np
from treelib import Node, Tree

from dama.game.dama import DamaGame
from dama.agents.placeholder import getPlaceholder
from dama.game.constants import Color
from dama.game.gameboard import Gameboard

import time

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
        state = State(parentBoard.gameboard, None, None)
        parentNode = Node(data=state)
        tree.add_node(parentNode)

    if game is None:
        game = DamaGame(board=parentBoard)

    for move, remove in zip(moveList, removeList):
        
        start = time.time()

        childBoard = Gameboard(gameboard=np.copy(parentBoard.gameboard))
        time1 = time.time()

        game.performMove(
            move, remove, temp_gameboard=childBoard
        )
        time2 = time.time()
        
        state = State(childBoard.gameboard, move, remove)
        node = Node(data=state)
        tree.add_node(node, parent=parentNode)
        time3 = time.time()

        player = getPlaceholder(color, opposite=True)
        res = game.get_all_legal_moves(player, temp_gameboard=childBoard)
        time4 = time.time()

        # print("Time to copy board     : {:4.0f} ms".format(1000*(time1 - start)))
        # print("Time to perform move   : {:4.0f} ms".format(1000*(time2 - time1)))
        # print("Time to add to tree    : {:4.0f} ms".format(1000*(time3 - time2)))
        # print("Time to get next moves : {:4.0f} ms".format(1000*(time4 - time3)))
        # print()

        if depth is not 0:
            getMoveTree(
                childBoard, res['move'], res['remove'], player.color, depth - 1,
                tree, node
            )

    return tree