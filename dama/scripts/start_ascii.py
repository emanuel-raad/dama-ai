from dama.game.dama2 import DamaGame
from dama.agents.human import Human
from dama.agents.alphaBeta import AlphaBeta
from dama.agents.random import Random
from dama.game.constants import Color

if __name__ == '__main__':
    game = DamaGame()

    # player1 = Human(Color.WHITE)
    # player2 = Human(Color.BLACK)

    # player2 = AlphaBeta(Color.BLACK, movesAhead=2)

    player1 = Random(Color.WHITE)
    player2 = Random(Color.BLACK)

    game.setPlayer(player1)
    game.setPlayer(player2)

    game.start()