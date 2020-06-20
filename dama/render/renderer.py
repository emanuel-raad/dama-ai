from abc import ABC, abstractmethod
from typing import List

from dama.game.bitboard import Bitboard
from dama.game.move import MoveNode

class Renderer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def drawBoard(self, board:Bitboard):
        pass

    @abstractmethod
    def animateMove(self, move:List[MoveNode]):
        pass

    @abstractmethod
    def requestMoveFromPlayer(self, board, player, legalMoves:List[List[MoveNode]]):
        pass

    @abstractmethod
    def animateWinner(self, winner):
        pass

    @abstractmethod
    def cleanup(self):
        pass
