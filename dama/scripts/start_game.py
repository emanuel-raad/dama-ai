from dama.game import dama
from dama.agents.human import Human
from dama.agents.random import Random
from dama.game.constants import Color

if __name__ == '__main__':

    print("Hello World!")

    game = dama.DamaGame()

    # player1 = Human(Color.BLACK)
    player1 = Random(Color.BLACK)
    # player2 = Human(Color.WHITE)
    player2 = Random(Color.WHITE)

    game.setAgent(player1)
    game.setAgent(player2)

    # If not set, then the white player starts first
    # game.setStartingPlayer(player1)

    game.start_game()