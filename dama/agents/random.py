from dama.agents.player import Player
from random import randrange

class Random(Player):
    def request_move(self, moveList, removeList):
        return randrange(len(moveList))