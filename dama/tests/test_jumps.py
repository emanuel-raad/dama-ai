from dama.game import dama
from dama.agents import player
from dama.game.constants import Color
import numpy as np

class Test():
    def __init__(self, player, board):
        self.player = player
        self.board = board
        self.damagame = dama.DamaGame()
        self.damagame.gameboard = board
    def show_jumps(self, position):
        res = self.damagame.get_piece_legal_move(self.player, position)
        res['tree'].show(data_property='position')

branching = np.array([
            [3, 0, 3, 0, 3, 0, 3, 0], #0
            [0, 3, 0, 3, 0, 3, 0, 3], #1
            [3, 0, 3, 0, 3, 0, 3, 0], #2
            [0, 3, 0, 3, 0, 3, 0, 3], #3
            [3, 0, 3, 1, 3, 0, 3, 0], #4
            [0, 3, 0, 3, 0, 3, 0, 3], #5
            [0, 0, 0, 0, 0, 0, 0, 0], #6
            [0, 0, 0, 0, 0, 0, 0, 0]  #7
        ])

branching2 = np.array([
            [1, 0, 1, 0, 1, 0, 1, 0], #0
            [0, 1, 0, 1, 0, 1, 0, 1], #1
            [1, 0, 1, 0, 1, 0, 1, 0], #2
            [0, 1, 0, 1, 0, 1, 0, 1], #3
            [1, 0, 1, 3, 1, 0, 1, 0], #4
            [0, 1, 0, 1, 0, 1, 0, 1], #5
            [0, 0, 0, 0, 0, 0, 0, 0], #6
            [0, 0, 0, 0, 0, 0, 0, 0]  #7
        ])

if __name__ == '__main__':
    
    print("Testing jumps...!")

    white = player.Player(Color.WHITE)
    black = player.Player(Color.BLACK)

    test1 = Test(white, branching)
    test1.show_jumps(np.array([3, 3]))

    test2 = Test(black, branching2)
    test2.show_jumps(np.array([4, 3]))