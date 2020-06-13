import time

import numpy as np
from treelib import Node, Tree

from dama.agents import helper
from dama.agents.placeholder import getPlaceholder
from dama.agents.player import Player


class AlphaBeta(Player):

    def __init__(self, color, moveCache=None, movesAhead = 2):
        super().__init__(color, moveCache=moveCache)

        # Maybe make moves ahead more dynamic
        # At the beginning of the game, it is small
        # Towards the end, when there are less pieces, it is large
        self.movesAhead = movesAhead

    def evaluate(self, board, color):
        metrics = board.metrics(getPlaceholder(color))

        score = (
              2 * metrics['myPieces'] - 1 * metrics['opponentPieces']
            + 4 * metrics['myPromoted'] - 5 * metrics['opponentPromoted']
        )

        return score

    def alphaBeta(self, tree, node, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or node.is_leaf():
            # always evaluate as if you are the player at the tree root
            color = tree.get_node(tree.root).data.color
            return self.evaluate(node.data.gameboard, color)

        if maximizingPlayer:
            value = np.NINF
            for child_id in node.fpointer:
                child_node = tree.get_node(child_id)
                value = max(value, self.alphaBeta(tree, child_node, depth - 1, alpha, beta, False))
                child_node.data.value = value
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        else:
            value = np.Inf
            for child_id in node.fpointer:
                child_node = tree.get_node(child_id)
                value = min(value, self.alphaBeta(tree, child_node, depth - 1, alpha, beta, True))
                child_node.data.value = value
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def request_move(self, board, moveList, removeList):
        
        time1 = time.time()
        tree = helper.getMoveTree(
            board, moveList, removeList, self.color, self.movesAhead, moveCache=self.moveCache
        )
        time2 = time.time()
        totalTime = 1000 * (time2 - time1)

        print("Looked at {} possible boards in {}ms".format(tree.size(), totalTime))

        # print
        # (
        #     'Final Score: {}'.format
        #     (
        #         self.alphaBeta(tree, tree.get_node(tree.root), self.movesAhead + 1, np.NINF, np.Inf, True)
        #     )
        # )

        # Run search
        self.alphaBeta(tree, tree.get_node(tree.root), tree.depth(), np.NINF, np.Inf, True)

        best_move = None
        best_value = np.NINF

        for child_id in tree.get_node(tree.root).fpointer:
            child_node = tree.get_node(child_id)
            value = child_node.data.value
            move = child_node.data.move

            if value is not None and value > best_value:
                best_value = value
                best_move = move

        # tree.show(data_property="value")
        # print(moveList)
        # print(best_move)
        choice = helper.getMoveFromMovelist(best_move, moveList)

        return choice
