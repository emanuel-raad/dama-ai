import time

import numpy as np
from treelib import Node, Tree

from dama.agents.player import Player

from dama.game.attack_routines import move_search
from dama.game.bitboard import countBoard

from dama.game.fen import movelist2fen

class AlphaBeta(Player):

    def __init__(self, color, movesAhead = 2):
        super().__init__(color)

        # Maybe make moves ahead more dynamic
        # At the beginning of the game, it is small
        # Towards the end, when there are less pieces, it is large
        self.movesAhead = movesAhead

    def evaluate(self, board):

        myPieces, myPromoted, oppPieces, oppPromoted = countBoard(board)

        # Add value depending on the positioning of the piece
        score = (
              1 * myPieces - 0.8 * oppPieces
            + 3 * myPromoted - 5 * oppPromoted
        )

        return score

    def alphaBeta(self, tree, node, depth, alpha, beta, maximizingPlayer, bestValue, bestValueID=None):
        if depth == 0 or node.is_leaf():
            # always evaluate as if you are the player at the tree root
            return self.evaluate(node.data.bitboards), None

        if maximizingPlayer:
            value = np.NINF
            for child_id in node.fpointer:
                child_node = tree.get_node(child_id)
                value = max(value, self.alphaBeta(tree, child_node, depth - 1, alpha, beta, False, bestValue, bestValueID)[0])
                if value > bestValue:
                    bestValue = value
                    bestValueID = child_id

                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, bestValueID

        else:
            value = np.Inf
            for child_id in node.fpointer:
                child_node = tree.get_node(child_id)
                value = min(value, self.alphaBeta(tree, child_node, depth - 1, alpha, beta, True, bestValue, bestValueID)[0])
                if value > bestValue:
                    bestValue = value
                    bestValueID = child_id
                
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, bestValueID

    def request_move(self, board, legalMoves):
        
        tree = move_search(board, self.movesAhead)

        # Run search
        value, bestValueID = self.alphaBeta(tree, tree.get_node(tree.root), tree.depth(), np.NINF, np.Inf, True, np.NINF)

        for i, moveNode in enumerate(tree.all_nodes_itr()):
            if tree.is_ancestor(moveNode.identifier, bestValueID) \
                and tree.root is not moveNode.identifier \
                or moveNode.identifier == bestValueID:
                
                # print("I want to perform: {}".format(movelist2fen(moveNode.data.moveList)))
                
                # This works because the first depth that we generate here and the first depth
                # of the legal moves will always be the same
                # Subtract 1 to get rid of the index of the root node
                
                return i - 1