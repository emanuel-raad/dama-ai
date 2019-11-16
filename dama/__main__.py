from dama.game import dama
from dama.agents import player
from dama.game.constants import Color

if __name__ == '__main__':
    print("Hello World!")

    damagame = dama.DamaGame()

    white = player.Player(Color.WHITE)
    black = player.Player(Color.BLACK)

    print(damagame.gameboard)

    print()
    print("WHITE")
    print(damagame.get_piece_legal_move(white, [1, 1]))
    print(damagame.get_piece_legal_move(white, [2, 1]))
    print(damagame.get_piece_legal_move(white, [3, 1]))
    
    print()
    print("BLACK")
    print(damagame.get_piece_legal_move(black, [5, 5]))
    print(damagame.get_piece_legal_move(black, [6, 6]))
    print(damagame.get_piece_legal_move(black, [7, 7]))