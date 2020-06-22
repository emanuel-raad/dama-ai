from dama.game.constants import Pieces
from dama.game.constants import Color

from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, color):
        self.color = color
        self.timeList = []
        self.type = 'AI'

    @abstractmethod
    def request_move(self, board, moveList):
        pass

    def cleanup(self):
        pass

    def get_color(self, opposite=True):
        if not opposite:
            return self.color
        else:
            if self.color == Color.WHITE:
                return Color.BLACK
            else:
                return Color.WHITE