from dama.game.constants import Pieces
from dama.game.constants import Color

from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def request_move(self, moveList, removeList):
        pass