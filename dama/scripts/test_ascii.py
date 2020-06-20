from dama.game.attack_routines import get_moves_from_tree, move_search
from dama.game.bitboard import get_starting_board, perform_move_board
from dama.render.ascii import Ascii
from dama.agents.human import Human
from dama.game.constants import Color

if __name__ == '__main__':
    renderer = Ascii()

    b = get_starting_board()

    renderer.drawBoard(b)
    print()

    moves = get_moves_from_tree(move_search(b, 0))

    choice = renderer.requestMoveFromPlayer(b, Human(Color.WHITE), moves)

    b = perform_move_board(moves[choice], b)

    renderer.drawBoard(b)
    print()
