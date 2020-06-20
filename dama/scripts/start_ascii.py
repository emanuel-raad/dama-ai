from dama.game.dama2 import DamaGame
from dama.agents.human import Human
from dama.agents.alphaBeta import AlphaBeta
from dama.agents.random import Random
from dama.game.constants import Color
from dama.game.bitboard import numpyboard2bitboard
import numpy as np

if __name__ == '__main__':

    b = numpyboard2bitboard(np.array([
        [0, 2, 0, 0, 0, 0, 0, 0,],
        [0, 0, 0, 0, 0, 0, 0, 0,],
        [0, 0, 0, 0, 0, 0, 0, 0,],
        [0, 0, 0, 3, 0, 0, 0, 0,],
        [0, 0, 0, 3, 0, 0, 0, 0,],
        [0, 0, 0, 3, 0, 0, 0, 0,],
        [0, 0, 0, 0, 0, 0, 0, 0,],
        [0, 0, 0, 0, 0, 0, 0, 0,],
    ]))


    game = DamaGame(bitboard=b)

    player1 = Human(Color.WHITE)
    # player2 = Human(Color.BLACK)

    # player2 = AlphaBeta(Color.BLACK, movesAhead=2)

    # player1 = Random(Color.WHITE)
    player2 = Random(Color.BLACK)

    # TODO : no moves are being found for the sliding king

    game.setPlayer(player1)
    game.setPlayer(player2)

    game.start()