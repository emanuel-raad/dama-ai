from dama.agents.player import Player
from dama.agents import helper

class AlphaBeta(Player):

    def __init__(self, color, movesAhead = 2):
        super().__init__(color)

        # Maybe make moves ahead more dynamic
        # At the beginning of the game, it is small
        # Towards the end, when there are less pieces, it is large
        self.movesAhead = movesAhead

    def request_move(self, board, moveList, removeList):
        
        tree = helper.getMoveTree(board, moveList, removeList, self.color, self.movesAhead)
        
        return tree