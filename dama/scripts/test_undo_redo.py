from dama.agents.human import Human

from dama.game.constants import Color
from dama.game.gameboard import Gameboard
from dama.game.move import Move, MoveType
from dama.game.constants import Pieces

import numpy as np

if __name__ == '__main__':
    gameboard = Gameboard()

    move1 = Move(
        [np.array([5, 0]), np.array([4, 0])],
        [],
        [],
        Color.WHITE
    )

    move2 = Move(
        [np.array([2, 0]), np.array([3, 0])],
        [],
        [],
        Color.WHITE
    )

    move3 = Move(
        [np.array([4, 0]), np.array([2, 0]), np.array([0, 0])],
        [np.array([3, 0]), np.array([1, 0])],
        [Pieces.BLACK, Pieces.BLACK],
        Color.WHITE
    )

    gameboard.print_board()
    print('--------------------------')
    
    gameboard.performMove(move1)
    gameboard.print_board()
    print('--------------------------')
    
    gameboard.performMove(move2)
    gameboard.print_board()
    print('--------------------------')

    gameboard.performMove(move3)
    gameboard.print_board()
    print('--------------------------')

    gameboard.undoMove()
    gameboard.undoMove()
    gameboard.undoMove()
    gameboard.undoMove()
    gameboard.print_board()
    print('--------------------------')