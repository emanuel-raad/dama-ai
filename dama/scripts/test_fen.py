import dama.game.fen as fen
from dama.game.bitboard import print_bitboard
from dama.game.bitboard_constants import PawnPromote

# TODO: validate this more
if __name__ == '__main__':
    assert fen.pos2fen(0) == 'a1'
    assert fen.pos2fen(63) == 'h8'
    assert fen.pos2fen(27) == 'd4'

    assert fen.fen2pos('a1') == 0
    assert fen.fen2pos('h8') == 63
    assert fen.fen2pos('d4') == 27

    a = fen.bitboard2fen(PawnPromote)
    print(a)

    bitboard = fen.fen2bitboard(a)
    print_bitboard([ bitboard.myPawn, bitboard.oppPawn ])