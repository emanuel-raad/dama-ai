from typing import List

import numpy as np

from dama.game.bitboard import Bitboard, bitboard2numpyboard
from dama.game.move import MoveNode
from dama.render.renderer import Renderer
from dama.game.fen import movelist2fen, flipFen

class Ascii(Renderer):
    def setup(self):
        ''' Nothing to setup
        '''
        pass

    def drawBoard(self, board:Bitboard):
        npBoard = bitboard2numpyboard(board)

        print("   a  b  c  d  e  f  g  h")
        for i, row in enumerate(npBoard):
            print("{} {}".format(-1*i + 8, row))
        print("   a  b  c  d  e  f  g  h")

    def animateMove(self, move:List[MoveNode]):
        ''' I could print some text here explaining the move,
            but otherwise nothing really else to animate
        '''
        pass

    def requestMoveFromPlayer(self, board, player, legalMoves:List[List[MoveNode]]):
        choice = 0

        if player.type == 'Human':
            repeat = True

            while repeat:
                for i, move in enumerate(legalMoves):
                    fen = movelist2fen(move)[0]
                    print("{} | {}".format(i, fen))
                print('--------------')
                print('Pick a move')

                try:
                    choice = int(input(">> "))
                except ValueError:
                    print("Not a valid choice!")
                    print()

                if choice >= 0 and choice <= len(legalMoves) - 1:
                    repeat = False
        elif player.type == 'AI':
            choice = player.request_move(board, legalMoves)
            moveStr, capStr = movelist2fen(legalMoves[choice])
            print("I'm going to move   : {}".format(flipFen(moveStr)))
            print("I'm going to capture: {}".format(flipFen(capStr)))

        return choice
    
    def animateWinner(self, winner):
        ''' Print a nice message
        '''
        print('Congrats {} Player!!!!!!'.format(winner.color))
        pass

    def cleanup(self):
        ''' Nothing to clean up really
        '''
        pass
