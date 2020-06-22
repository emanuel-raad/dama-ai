import unittest

import dama.game.fen as fen
from dama.game.constants import Color
from dama.game.bitboard import print_bitboard, flip_color, Bitboard, initialize_board, perform_move_board
from dama.game.bitboard_constants import PawnPromote
from dama.agents.alphaBeta import AlphaBeta

# TODO: validate this more
if __name__ == '__main__': 
    # unittest.main()
    myPawn = initialize_board([1, 2])
    myKing = 0
    oppPawn = initialize_board([5, 6])
    oppKing = 0
    board = Bitboard(myPawn, myKing, oppPawn, oppKing)

    ai = AlphaBeta(Color.WHITE)
    m = ai.request_move(board)
    # print(fen.movelist2fen(m.data.moveList))

    board2 = perform_move_board(m.data.moveList, board)
    print_bitboard([ board.board, board2.board ])
    print()

    m2 = ai.request_move(flip_color(board2))
    board3 = perform_move_board(m2.data.moveList, flip_color(board2))
    board3 = flip_color(board3)
    print_bitboard([ board2.board, board3.board ])
