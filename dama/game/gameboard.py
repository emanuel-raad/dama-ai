import numpy as np
from dama.agents.player import Player
from dama.game.constants import Pieces
from dama.game.constants import Color

class Gameboard:
    '''
    Represent the game board.
    '''
    def __init__(self,
                rows = 8,
                cols = 8,
                gameboard = None
                ):

        self.rows = rows
        self.cols = cols

        if gameboard is None:
            self.initialize_gameboard()
        else:
            self.gameboard = gameboard

    def initialize_gameboard(self):
        self.gameboard = np.zeros((self.rows, self.cols), dtype='uint8')
        self.gameboard[1:3] = Pieces.BLACK
        self.gameboard[5:7] = Pieces.WHITE

    def promote_piece(self, position):
        pass

    def remove_piece(self, position):
        self.gameboard[position[0], position[1]] = Pieces.EMPTY

    def move_piece(self, startPosition, endPosition):
        piece = self.at(startPosition)
        self.remove_piece(startPosition)
        self.gameboard[endPosition[0], endPosition[1]] = piece

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

    def at(self, position):
        if not self.is_outside_board(position):
            return self.gameboard[position[0], position[1]]
        else:
            raise IndexError("Position outside of board")

    def player_owns_piece(self, player, position):
        piece = self.at(position)
        
        if player.color == Color.WHITE:
            if piece == Pieces.WHITE or piece == Pieces.WHITE_PROMOTED:
                return True
        elif player.color == Color.BLACK:
            if piece == Pieces.BLACK or piece == Pieces.BLACK_PROMOTED:
                return True
        
        return False

    def opponents_between_two_positions(self, player, p1, p2):
        if p1[0] == p2[0]:
            x1 = p1[0]
            y1 = min(p1[1], p2[1])
            y2 = max(p1[1], p2[1])
            res = self.gameboard[x1,:][y1:y2+1]
        elif p1[1] == p2[1]:
            y1 = p2[1]
            x1 = min(p1[0], p2[0])
            x2 = max(p1[0], p2[0])
            res = self.gameboard[:,y1][x1:x2+1]

        count = 0
        for i in res:
            if player.color == Color.WHITE:
                if i == Pieces.BLACK or i == Pieces.BLACK_PROMOTED:
                    count = count + 1
            elif player.color == Color.BLACK:
                if i == Pieces.WHITE or i == Pieces.WHITE_PROMOTED:
                    count = count + 1
        
        return count

    def metrics(self, player):

        '''
        Could loop over the board once, instead of four times
        '''

        if player.color == Color.BLACK:
            myPieces = np.count_nonzero(self.gameboard == Pieces.BLACK)
            myPromoted = np.count_nonzero(self.gameboard == Pieces.BLACK_PROMOTED)
            opponentPieces = np.count_nonzero(self.gameboard == Pieces.WHITE)
            opponentPromoted = np.count_nonzero(self.gameboard == Pieces.WHITE_PROMOTED)
        else:
            myPieces = np.count_nonzero(self.gameboard == Pieces.WHITE)
            myPromoted = np.count_nonzero(self.gameboard == Pieces.WHITE_PROMOTED)
            opponentPieces = np.count_nonzero(self.gameboard == Pieces.BLACK)
            opponentPromoted = np.count_nonzero(self.gameboard == Pieces.BLACK_PROMOTED)

        return {
            'myPieces' : myPieces,
            'myPromoted' : myPromoted,
            'opponentPieces' : opponentPieces,
            'opponentPromoted' : opponentPromoted
        }

    def print_board(self):

        header = np.array(list(range(self.cols)))

        print("{} {}".format(" ", header))
        for i, row in enumerate(self.gameboard):
            print("{} {}".format(i, row))