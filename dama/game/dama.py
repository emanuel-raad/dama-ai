import numpy as np
from dama.agents.player import Player
from dama.game.constants import Pieces
from dama.game.constants import Color

class DamaGame:
    def __init__(self):
        self.n_turns = 0
        self.initialize_gameboard()

    def initialize_gameboard(self):
        self.rows = 8
        self.cols = 8
        self.gameboard = np.zeros((self.rows, self.cols), dtype='uint8')
        self.gameboard[1:3] = Pieces.WHITE
        self.gameboard[5:7] = Pieces.BLACK

    def promote_piece(self, position):
        pass

    def remove_piece(self, position):
        pass

    def move_piece(self, position):
        pass

    def get_all_legal_moves(self, player):
        
        legal_moves = []

        for x in range(0, self.rows):
            for y in range(0, self.cols):
                if self.player_owns_piece(player, [x, y]):
                    pass
                else:
                    pass

        return legal_moves

    def is_promoted(self, position):
        if ((self.gameboard[position[0], position[1]] == Pieces.WHITE_PROMOTED) or 
            (self.gameboard[position[0], position[1]] == Pieces.BLACK_PROMOTED)):
            return True
        else:
            return False

    def is_outside_board(self, position):
        for pos in position:
            if pos < 0 or pos > 7:
                return True
        return False

    def player_owns_piece(self, player, position):
        # if self.is_outside_board(position):
        #     return False
        
        piece = self.gameboard[position[0], position[1]]
        
        if player.color == Color.WHITE:
            if piece == Pieces.WHITE or piece == Pieces.WHITE_PROMOTED:
                return True
        elif player.color == Color.BLACK:
            if piece == Pieces.BLACK or piece == Pieces.BLACK_PROMOTED:
                return True
        
        return False        

    def get_piece_legal_move(self, player, position):

        piece_legal_moves = []

        if not self.player_owns_piece(player, position):
            print("Dont own piece {} at {}".format(
                self.gameboard[position[0], position[1]], position)
            )
            return piece_legal_moves

        if player.color == Color.WHITE:
            adjacent = np.array([[1, 0], [0, -1], [0, 1]])
        elif player.color == Color.BLACK:
            adjacent = np.array([[-1, 0], [0, -1], [0, 1]])
        
        for i in adjacent:

            if self.is_promoted(position):
                # Promoted piece moves
                
                pass
            else:
                # Normal piece moves

                adjacent_piece = position + i
                # print("Adjacent Piece: {}".format(adjacent_piece))
                if self.is_outside_board(adjacent_piece):
                    # print("Adjacent Piece outside of board")
                    continue

                if self.player_owns_piece(player, adjacent_piece):
                    # You own the piece, can't move there
                    continue
                
                elif (not self.player_owns_piece(player, adjacent_piece)) and (self.gameboard[adjacent_piece[0], adjacent_piece[1]] != Pieces.EMPTY):
                    # There is a piece there that you don't own
                    next_adjacent_piece = adjacent_piece + i
                    if self.is_outside_board(next_adjacent_piece):
                        continue

                    if next_adjacent_piece == Pieces.EMPTY and self.gameboard[adjacent_piece[0], adjacent_piece[1]] != Pieces.EMPTY:
                        piece_legal_moves.append(next_adjacent_piece)
                
                elif self.gameboard[adjacent_piece[0], adjacent_piece[1]] == Pieces.EMPTY:
                    # There is an empty piece you can move to
                    piece_legal_moves.append(adjacent_piece)

        return piece_legal_moves



    # def check_win_state(self, Player):
    def check_win_state(self):
        '''
        1. Opponent has no legal moves (all pieces are captured, or completely blocked)
        2. King vs. single man
        '''
        pass
    
    def increment_turn(self):
        self.n_turns += 1