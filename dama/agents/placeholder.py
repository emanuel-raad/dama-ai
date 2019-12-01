from dama.agents.player import Player
from dama.game.constants import Color

class Placeholder(Player):
    def request_move(self, board, moveList, removeList):
        pass


WHITE_PLACEHOLDER = Placeholder(Color.WHITE)
BLACK_PLACEHOLDER = Placeholder(Color.BLACK)

def getPlaceholder(color, opposite=False):

    if not opposite:
        if color == Color.WHITE:
            return WHITE_PLACEHOLDER
        elif color == Color.BLACK:
            return BLACK_PLACEHOLDER
    else:
        if color == Color.WHITE:
            return BLACK_PLACEHOLDER
        elif color == Color.BLACK:
            return WHITE_PLACEHOLDER