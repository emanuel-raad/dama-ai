import time

import numpy as np

from dama.agents.alphaBeta import AlphaBeta
from dama.agents.human import Human
from dama.agents.random import Random
from dama.game import dama
from dama.game.constants import Color

if __name__ == '__main__':

    print("Hello World!")

    board = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ])

    game = dama.DamaGame(board=board)

    game.gameboard.print_board()
    player1 = AlphaBeta(Color.BLACK, movesAhead=0)

    res = game.get_all_legal_moves(player1)

    start_time = time.time()
    choice = player1.request_move(game.gameboard, res['move'], res['remove'])
    print(choice)
    end_time = time.time()

    # print("Completed in {:.4f} seconds".format(end_time-start_time))
