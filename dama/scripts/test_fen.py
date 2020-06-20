import unittest

import dama.game.fen as fen
from dama.game.bitboard import print_bitboard, flip_color, Bitboard, initialize_board
from dama.game.bitboard_constants import PawnPromote, StartingBoard
from dama.game.attack_routines import move_search, listFromTree, get_moves_from_tree

class TestFenMethods(unittest.TestCase): 

    def setUp(self): 
        pass

    def test_pos2fen(self):
        assert fen.pos2fen(0) == 'a1'
        assert fen.pos2fen(63) == 'h8'
        assert fen.pos2fen(27) == 'd4'
        assert fen.pos2fen(16) == 'a3'
        assert fen.pos2fen(17) == 'b3'

    def test_fen2pos(self):
        assert fen.fen2pos('a1') == 0
        assert fen.fen2pos('h8') == 63
        assert fen.fen2pos('d4') == 27
        assert fen.fen2pos('a3') == 16
        assert fen.fen2pos('b3') == 17

    def test_bitboard2fen(self):
        assert fen.bitboard2fen(StartingBoard) == '8/pppppppp/pppppppp/8/8/PPPPPPPP/PPPPPPPP/8'

    def test_fen2bitboard(self):
        bitboard = fen.fen2bitboard('8/pppppppp/pppppppp/8/8/PPPPPPPP/PPPPPPPP/8')
        assert bitboard.myPawn == 0b0000000000000000000000000000000000000000111111111111111100000000
        assert bitboard.oppPawn == 0b0000000011111111111111110000000000000000000000000000000000000000

# TODO: validate this more
if __name__ == '__main__': 
    unittest.main()
    # print(fen.flipFen('a1-a2-a3'))
    # myPawn = initialize_board([1, 2])
    # myKing = 0
    # oppPawn = initialize_board([5, 6])
    # oppKing = 0
    # board = Bitboard(myPawn, myKing, oppPawn, oppKing)

    # movelist = get_moves_from_tree(move_search(board, 0))

    # # This presents the moves in a human readable format
    # for i, move in enumerate(movelist):
    #     # skip the root node, it's useless
    #     if i != 0:
    #         m, c = fen.movelist2fen(movelist[i])
    #         print("Move to: {}".format(m))
    #         print("Capture: {}".format(c))
    #         print()