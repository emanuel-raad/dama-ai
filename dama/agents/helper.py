import numpy as np
import time
import hashlib
import pickle
import os
import logging
from treelib import Node, Tree

from dama.game.dama import DamaGame
from dama.agents.placeholder import getPlaceholder
from dama.game.constants import Color
from dama.game.gameboard import Gameboard
from dama.game.fenController import board2fen

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
    def __init__(self, gameboard, move, remove, color, value = None):
        self.gameboard = gameboard
        self.move = move
        # self.remove = remove
        self.color = color
        self.value = value

class MoveCache():
    def __init__(self, path=None, buildCache=False):
        self.path = path
        self.buildCache = buildCache

        # Loads the cache as moveDict
        self.load()

        if not os.path.exists(self.path):
            self.moveDict = {}
        else:
            self.load()
    
    def save(self):
        if self.buildCache:
            # print("Saving")
            with open(self.path, 'wb') as cacheFile:
                pickle.dump(self.moveDict, cacheFile)
    
    def load(self):
        if not os.path.exists(self.path):
            self.moveDict = {}
        else:
            with open(self.path, 'rb') as cacheFile:
                self.moveDict = pickle.load(cacheFile)

        # print("loaded: {}".format(self.moveDict))
    
    @staticmethod
    def hashBoard(board):
        return board2fen(board)

    def cacheMove(self, key, tree):
        if self.buildCache:
            self.moveDict[key] = tree

    def getTree(self, key):
        return self.moveDict[key]

    def contains(self, key):
        return key in self.moveDict

    def containsBoard(self, board):
        key = self.hashBoard(board)
        return self.contains(key)

def getMoveTree(
    parentBoard, moveList, removeList, color, depth,
    tree = None, parentNode = None, game = None, moveCache = None
    ):

    # print("Depth: {}".format(depth))

    if moveCache is None:
        return buildMoveTree(
            parentBoard, moveList, removeList, color, depth,
            tree = None, parentNode = None, game = None
        )

    key = moveCache.hashBoard(parentBoard.gameboard)
    print(key)

    if moveCache.contains(key):
        print("Contains key")
        return moveCache.getTree(key)
    else:
        print("Does not contain key")
        tree = buildMoveTree(
            parentBoard, moveList, removeList, color, depth,
            tree = None, parentNode = None, game = None
            )

        if moveCache.buildCache:
            moveCache.cacheMove(key, tree)
        
        return tree

def buildMoveTree(
    parentBoard, moveList, removeList, color, depth,
    tree = None, parentNode = None, game = None
    ):

    if tree is None:
        tree = Tree()
        state = State(parentBoard, None, None, color)
        parentNode = Node(data=state)
        tree.add_node(parentNode)

    if game is None:
        game = DamaGame(board=parentBoard)

    average_get_legal_moves_times = []

    for move, remove in zip(moveList, removeList):
        
        start = time.time()

        childBoard = Gameboard(gameboard=np.copy(parentBoard.gameboard))
        time1 = time.time()

        game.performMove(
            move, remove, temp_gameboard=childBoard
        )
        time2 = time.time()
        
        state = State(childBoard, move, remove, color)
        node = Node(data=state)
        tree.add_node(node, parent=parentNode)
        time3 = time.time()

        player = getPlaceholder(color, opposite=True)
        res = game.get_all_legal_moves(player, temp_gameboard=childBoard)
        time4 = time.time()

        average_get_legal_moves_times.append(1000*(time4 - time3))

        # logging.debug("Time to copy board     : {:4.0f} ms".format(1000*(time1 - start)))
        # logging.debug("Time to perform move   : {:4.0f} ms".format(1000*(time2 - time1)))
        # logging.debug("Time to add to tree    : {:4.0f} ms".format(1000*(time3 - time2)))
        # logging.debug("Time to get next moves : {:4.0f} ms".format(1000*(time4 - time3)))

        if depth is not 0:
            buildMoveTree(
                childBoard, res['move'], res['remove'], player.color, depth - 1,
                tree, node
            )

    logging.debug("Average time for each move: {}ms".format(np.average(average_get_legal_moves_times)))

    return tree

def getMoveFromMovelist(move, moveList):
    for i, row in enumerate(moveList):
        if np.all(np.equal(move, row)):
            return i