from dama.game.attack_routines import get_moves_from_tree, move_search
from dama.game.bitboard import get_starting_board, perform_move_board
from dama.game.bitboard_constants import KingZigzag, StartingBoard
from dama.render.ascii import Ascii

if __name__ == '__main__':
    renderer = Ascii()

    b = get_starting_board()

    renderer.drawBoard(b)
    print()

    moves = get_moves_from_tree(move_search(b, 0))

    choice = renderer.requestMove(moves)

    b = perform_move_board(moves[choice], b)

    renderer.drawBoard(b)
    print()
