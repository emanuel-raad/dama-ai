from dama.game.constants import Pieces
from dama.game.constants import Color

from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def request_move(self, board, moveList, removeList):
        pass

    def get_color(self, opposite=True):
        if not opposite:
            return self.color
        else:
            if self.color == Color.WHITE:
                return Color.BLACK
            else:
                return Color.WHITE