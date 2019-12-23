from dama.game import dama

from dama.agents.human import Human
from dama.agents.random import Random
from dama.agents.alphaBeta import AlphaBeta
from dama.agents.helper import MoveCache

from dama.game.constants import Color

if __name__ == '__main__':

    print("Hello World!")

    game = dama.DamaGame()

    # Two Humans
    # player1 = Human(Color.BLACK)
    # player2 = Human(Color.WHITE)

    # Human and Random
    # player1 = Human(Color.BLACK)
    # player2 = Random(Color.WHITE)

    # Two Randoms
    # player1 = Random(Color.BLACK)
    # player2 = Random(Color.WHITE)

    # AlphaBeta and Random
    path = 'opening_moves_3ahead.cache'
    moveCache = MoveCache(path=path, buildCache = False)
    player1 = AlphaBeta(Color.BLACK, moveCache=moveCache, movesAhead=2)

    player2 = Random(Color.WHITE)

    game.setAgent(player1)
    game.setAgent(player2)

    # If not set, then the white player starts first
    # game.setStartingPlayer(player1)

    game.start_game()