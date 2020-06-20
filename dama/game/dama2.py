import numpy as np
import os

from dama.agents.player import Player
from dama.game.constants import Color

from dama.game.bitboard import Bitboard, initialize_board, print_bitboard, flip_color, get_starting_board, perform_move_board, countBoard
from dama.game.attack_routines import move_search, get_moves_from_tree
from dama.render.renderer import Renderer
from dama.render.ascii import Ascii
from dama.game.fen import movelist2fen

import time
import logging

class DamaGame:
    def __init__(self, renderer=Ascii(), bitboard=None, parallel=True):
        if bitboard is None:
            self.bitboard = get_starting_board()
        else:
            self.bitboard = bitboard

        self.parallel = parallel

        self.n_turns = 0

        # White, true. Black, false
        self.activePlayer = True
        self.startingPlayer = True

        self.white_player = None
        self.black_player = None
        self.currentPlayer = None

        self.renderer = renderer

        self.running = False

        self.winner = None

        # Add a game logger

    def setPlayer(self, player):
        if player.color == Color.WHITE:
            self.white_player = player
        elif player.color == Color.BLACK:
            self.black_player = player
        else:
            raise Exception('Wrong player color!')

    def check_players(self):
        return self.white_player is not None and self.black_player is not None

    def increment_turn(self):
        self.n_turns += 1

    def decrement_turn(self):
        self.n_turns -= 1

    def check_win_state(self, board, legalMoves):
        if len(legalMoves[0]) == 0:
            return True

        nMyPawn, nMyKing, nOppPawn, nOppKing = countBoard(board)
        if nMyPawn == 1 and nMyKing == 0 and nOppPawn == 0 and nOppKing == 1:
            return True

        return False

    def get_other_player(self, player):
        if player == self.white_player:
            return self.black_player
        else:
            return self.white_player

    def start(self, startingPlayer = True):
        self.activePlayer = startingPlayer

        if not self.check_players():
            raise Exception('Not all players set!')

        self.running = True
        
        counter = 0

        while self.running:

            # Process ######################################################
            
            # Count turn
            self.increment_turn()
            
            # Set active player
            if self.activePlayer:
                self.currentPlayer = self.white_player
            else:
                self.currentPlayer = self.black_player

            # Flip board, except for the first time
            if self.n_turns > 1:
                self.bitboard = flip_color(self.bitboard)

            # Draw ######################################################
            print('------------------------------------')
            print("Turn: {}".format(self.currentPlayer.color))
            if self.activePlayer == self.startingPlayer:
                self.renderer.drawBoard(self.bitboard)
            else:
                self.renderer.drawBoard(flip_color(self.bitboard))

            legalMoves = get_moves_from_tree(move_search(self.bitboard, 0, forceParallel=self.parallel, debug=True))

            # check win state
            if self.check_win_state(self.bitboard, legalMoves):
                if self.activePlayer:
                    self.winner = self.black_player
                else:
                    self.winner = self.white_player
                
                self.running = False
                break

            # should we request moves from the player instead of the renderer?
            # maybe pass the active player to the renderer, and have it handle it appropriately
            
            choice = self.renderer.requestMoveFromPlayer(self.bitboard, self.currentPlayer, legalMoves)

            # Log board here

            # print('I will perform: {}'.format(movelist2fen(legalMoves[choice])))
            self.bitboard = perform_move_board(legalMoves[choice], self.bitboard)
            self.renderer.animateMove(legalMoves[choice])
            
            # Update
            self.activePlayer = not self.activePlayer

        self.renderer.animateWinner(self.winner)
