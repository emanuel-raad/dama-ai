from dama.game import dama
from dama.agents.human import Human
from dama.agents.random import Random
from dama.agents.alphaBeta import AlphaBeta
from dama.game.constants import Color
import time
import numpy as np

if __name__ == '__main__':

    print("Hello World!")

    game = dama.DamaGame()
    # for i in range(game.gameboard.cols):
    #     game.gameboard.remove_piece(np.array([1, i]))
    #     game.gameboard.remove_piece(np.array([2, i]))
    #     game.gameboard.remove_piece(np.array([5, i]))
    #     game.gameboard.remove_piece(np.array([6, i]))

    game.gameboard.print_board()
    player1 = AlphaBeta(Color.BLACK)

    res = game.get_all_legal_moves(player1)

    start_time = time.time()
    choice = player1.request_move(game.gameboard, res['move'], res['remove'])
    print(choice)
    end_time = time.time()

    print("Completed in {:.4f} seconds".format(end_time-start_time))
