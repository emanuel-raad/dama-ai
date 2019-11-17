from dama.game import dama
from dama.agents import player
from dama.game.constants import Color
import numpy as np

if __name__ == '__main__':

    def reset():
        return np.array([
            [1, 3, 3, 0, 0, 0, 0, 0],
            [3, 3, 0, 1, 0, 0, 0, 0],
            [0, 3, 0, 0, 1, 0, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 0]
        ])

    print("Hello World!")

    damagame = dama.DamaGame()

    white = player.Player(Color.WHITE)
    black = player.Player(Color.BLACK)

    damagame.gameboard = np.array([
        [1, 3, 3, 0, 0, 0, 0, 0],
        [3, 3, 0, 1, 0, 0, 0, 0],
        [0, 3, 0, 0, 1, 0, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0],
        [3, 0, 0, 0, 0, 0, 0, 0]
    ])

    print("STARTING BOARD")
    print(damagame.gameboard)
    print()

    tests = [
        # [white, [[1, 1], [2, 1], [3, 0]]],
        # [black, [[5, 0], [6, 6], [7, 7]]],
        [black, np.array([[7, 0]])],
        [white, np.array([[0, 0]])]
    ]

    for i in tests:
        player = i[0]
        for position in i[1]:
            res = damagame.get_piece_legal_move(player, position)
            # print("Piece: {} Moves: {}".format(position, res['legal_moves']))
            res['tree'].show(data_property='position')
            damagame.gameboard = reset()
            # res['tree'].save2file('tree.txt', data_property='gameboard')

        print()