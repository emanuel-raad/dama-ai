from dama.game import dama
from dama.agents.human import Human
from dama.agents.random import Random
from dama.agents.alphaBeta import AlphaBeta
from dama.game.constants import Color
import time
import numpy as np

if __name__ == '__main__':

    print("Hello World!")

    board = np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [4, 1, 0, 0, 0, 0, 0, 0],
            ])

    default = np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [0, 0, 0, 0, 0, 0, 0, 0]    
    ])

    # board = np.array([
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 1, 0, 0, 0, 0],
    #             [0, 0, 0, 1, 0, 0, 0, 0],
    #             [0, 0, 1, 4, 1, 0, 1, 0],
    #             [0, 0, 0, 1, 0, 0, 0, 0],
    #             [0, 0, 0, 1, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #         ])

    game = dama.DamaGame(board=default)

    game.gameboard.print_board()
    player1 = Human(Color.BLACK)

    start_time = time.time()
    res = game.get_all_legal_moves(player1)
    end_time = time.time()

    # for m in res['move']:
    #     print(m)

    print("Completed in {:.4f} ms".format(1000*(end_time-start_time)))
    print("Number of paths: {}".format(len(res['move'])))
