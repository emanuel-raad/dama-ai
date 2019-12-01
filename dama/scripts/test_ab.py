from dama.game import dama
from dama.agents.human import Human
from dama.agents.random import Random
from dama.agents.alphaBeta import AlphaBeta
from dama.game.constants import Color
import time

if __name__ == '__main__':

    print("Hello World!")

    game = dama.DamaGame()

    player1 = AlphaBeta(Color.BLACK)

    res = game.get_all_legal_moves(player1)

    start_time = time.time()
    tree = player1.request_move(game.gameboard, res['move'], res['remove'])
    end_time = time.time()

    print("Completed in {:.4f} seconds".format(end_time-start_time))
    print("Looked at {} possible boards".format(tree.size()))