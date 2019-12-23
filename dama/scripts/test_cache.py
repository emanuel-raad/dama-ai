from dama.game import dama

from dama.agents.human import Human
from dama.agents.random import Random
from dama.agents.helper import MoveCache
from dama.agents.alphaBeta import AlphaBeta

from dama.game.constants import Color

import time
import numpy as np

if __name__ == '__main__':

    print("Hello World!")

    game = dama.DamaGame()

    game.gameboard.print_board()

    path = 'opening_moves_3ahead.cache'
    moveCache = MoveCache(path=path, buildCache = False)
    player1 = AlphaBeta(Color.BLACK, moveCache=moveCache, movesAhead=2)

    res = game.get_all_legal_moves(player1)

    start_time = time.time()

    choice = player1.request_move(game.gameboard, res['move'], res['remove'])
    
    player1.cleanup()

    print("Choice: {}".format(choice))
    end_time = time.time()

    print("Completed in {:.4f} seconds".format(end_time-start_time))
