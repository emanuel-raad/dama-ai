from dama.game.attack_routines import move_search, get_moves_from_tree, get_all_legal_moves_list
from dama.game.bitboard import numpyboard2bitboard, print_bitboard, bitboard2numpyboard
import numpy as np
from dama.game.fen import movelist2fen
from dama.render.ascii import Ascii

if __name__ == '__main__':
    
    numpy_boards = [
        np.array([
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 3, 3, 3, 3, 3, 3, 3,],
            [3, 3, 0, 0, 3, 0, 3, 3,],
            [3, 0, 0, 0, 3, 3, 0, 0,],
            [0, 0, 1, 0, 1, 1, 0, 1,],
            [0, 1, 1, 0, 1, 0, 1, 0,],
            [1, 1, 0, 1, 1, 1, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [3, 3, 3, 3, 3, 3, 3, 3,],
            [3, 3, 3, 3, 0, 3, 0, 3,],
            [0, 0, 0, 3, 0, 0, 3, 0,],
            [1, 0, 0, 0, 0, 0, 1, 0,],
            [1, 1, 1, 1, 1, 1, 0, 1,],
            [0, 1, 1, 1, 1, 1, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [1, 0, 0, 3, 3, 3, 3, 0,],
            [0, 0, 0, 0, 3, 0, 0, 0,],
            [0, 0, 0, 3, 0, 0, 0, 1,],
            [3, 3, 0, 1, 0, 0, 1, 0,],
            [0, 0, 0, 0, 1, 0, 1, 0,],
            [0, 0, 1, 0, 0, 0, 1, 1,],
            [4, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [2, 0, 0, 0, 2, 0, 0, 0,],
            [3, 0, 3, 3, 0, 3, 3, 3,],
            [0, 3, 3, 0, 0, 3, 3, 3,],
            [0, 0, 0, 3, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 1, 0, 0,],
            [1, 0, 1, 1, 0, 0, 1, 1,],
            [1, 1, 1, 1, 1, 1, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [3, 3, 3, 3, 3, 3, 3, 3,],
            [0, 3, 0, 3, 3, 3, 3, 3,],
            [0, 3, 3, 0, 0, 0, 0, 0,],
            [0, 0, 1, 0, 0, 1, 0, 0,],
            [1, 1, 1, 1, 1, 0, 1, 1,],
            [1, 1, 0, 1, 1, 1, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [0, 0, 0, 0, 0, 2, 0, 0,],
            [3, 3, 3, 3, 3, 3, 0, 0,],
            [0, 3, 3, 3, 0, 0, 0, 3,],
            [3, 0, 0, 0, 3, 0, 0, 0,],
            [0, 0, 1, 0, 0, 0, 0, 0,],
            [1, 1, 0, 1, 1, 1, 0, 1,],
            [1, 1, 1, 1, 0, 1, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [0, 0, 2, 0, 0, 0, 0, 0,],
            [3, 0, 0, 3, 3, 3, 3, 3,],
            [0, 0, 3, 3, 3, 0, 3, 3,],
            [0, 3, 0, 0, 0, 3, 0, 0,],
            [0, 0, 0, 0, 1, 0, 1, 0,],
            [1, 1, 0, 1, 0, 1, 0, 1,],
            [1, 1, 1, 1, 0, 1, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
        ]),

        np.array([
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 3, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 2, 0, 0, 1, 1, 0, 0,],
        ])

    ]

    render = Ascii()

    bitboards = [numpyboard2bitboard(b) for b in numpy_boards]

    for i, b in enumerate(bitboards):
        render.drawBoard(b)
        # moves = get_moves_from_tree(move_search(b, 0))
        moves = get_all_legal_moves_list(b)
        for m in moves:
            if len(m) > 0:
                print(movelist2fen(m)[0])
        print()
