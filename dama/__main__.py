from dama.game import dama
from dama.agents import player
from dama.game.constants import Color
from dama.tests.gameboards import simple_promoted
from dama.tests.gameboards import simple
from dama.tests.gameboards import empty
from dama.tests.gameboards import triple_jump
from dama.tests.gameboards import triple_jump_promoted
from dama.tests.gameboards import branching_black
from dama.tests.gameboards import zigzag
import numpy as np

if __name__ == '__main__':

    print("Hello World!")

    damagame = dama.DamaGame(board=zigzag)

    white = player.Player(Color.WHITE)
    black = player.Player(Color.BLACK)

    print("STARTING BOARD")
    print(damagame.gameboard.gameboard)
    print()

    tests = [
        [black, np.array([[7, 0]])],
        # [black, np.array([[5, 3]])]
    ]

    for i in tests:
        player = i[0]
        for position in i[1]:
            res = damagame.get_piece_legal_move(player, position)
            # print("Piece: {} Moves: {}".format(position, res['legal_moves']))
            res['tree'].show(data_property='position')
            damagame.gameboard = zigzag
            # res['tree'].save2file('tree.txt', data_property='gameboard')

        print()