from dama.game.constants import Pieces
from dama.game.constants import Color

from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, color, moveCache = None):
        self.color = color
        self.moveCache = moveCache
        self.timeList = []
        self.type = 'AI'

    @abstractmethod
    def request_move(self, board, moveList, removeList):
        pass

    def cleanup(self):
        if self.moveCache is not None:
            self.moveCache.save()

    def get_color(self, opposite=True):
        if not opposite:
            return self.color
        else:
            if self.color == Color.WHITE:
                return Color.BLACK
            else:
                return Color.WHITE