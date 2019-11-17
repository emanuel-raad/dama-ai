import numpy as np
from dama.agents.player import Player
from dama.game.constants import Pieces
from dama.game.constants import Color
from dama.game import direction
from treelib import Node, Tree

class State(object):
    def __init__(self, gameboard, position):
        self.gameboard = gameboard
        self.position = position
        self.tag = np.array2string(position)

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

    def remove_piece(self, gameboard, position):
        gameboard[position[0], position[1]] = Pieces.EMPTY

    def move_piece(self, gameboard, startPosition, endPosition):
        piece = self.at(gameboard, startPosition)
        self.remove_piece(gameboard, startPosition)
        gameboard[endPosition[0], endPosition[1]] = piece

    def get_all_legal_moves(self, gameboard, player):
        
        legal_moves = []

        for x in range(0, self.rows):
            for y in range(0, self.cols):
                if self.player_owns_piece(gameboard, player, [x, y]):
                    pass
                else:
                    pass

        return legal_moves

    def is_promoted(self, gameboard, position):
        if ((gameboard[position[0], position[1]] == Pieces.WHITE_PROMOTED) or 
            (gameboard[position[0], position[1]] == Pieces.BLACK_PROMOTED)):
            return True
        else:
            return False

    def is_outside_board(self, position):
        for pos in position:
            if pos < 0 or pos > 7:
                return True
        return False

    def at(self, gameboard, position):

        if not self.is_outside_board(position):
            return gameboard[position[0], position[1]]
        else:
            raise IndexError("Position outside of board")

    def player_owns_piece(self, gameboard, player, position): 
        piece = self.at(gameboard, position)
        
        if player.color == Color.WHITE:
            if piece == Pieces.WHITE or piece == Pieces.WHITE_PROMOTED:
                return True
        elif player.color == Color.BLACK:
            if piece == Pieces.BLACK or piece == Pieces.BLACK_PROMOTED:
                return True
        
        return False

    def get_piece_legal_move(
        self, player, position, 
        startPosition=None, piece_legal_moves = None, pieces_to_remove = None, gameboard = None,
        movetree = None, lastNode = None, canMove = True
    ):

        if piece_legal_moves is None:
            piece_legal_moves = []
        if pieces_to_remove is None:
            pieces_to_remove = []
        if gameboard is None:
            gameboard = self.gameboard
        
        state = State(gameboard, position)
        node = Node(tag=state.tag, data=state)
        

        if movetree is None:
            movetree = Tree()
        if self.player_owns_piece(gameboard, player, position):
            if lastNode is None:
                movetree.add_node(node)
                # print("Node: {}".format(node.data.tag))
                # print("ROOT NODE")
                # print(node.data.gameboard)
                # print()
            else:
                movetree.add_node(node, parent=lastNode)    
                # print("Node: {}".format(node.data.tag))
                # print("Parent: {}".format(movetree.parent(node.identifier).data.tag))
                # print(node.data.gameboard)
                # print()

        if self.player_owns_piece(gameboard, player, position):

            valid_directions = direction.get_valid_directions(
                startPosition, position, player.color, self.is_promoted(gameboard, position)
            )
            
            for i in valid_directions:
                
                if self.is_promoted(gameboard, position):
                    # Promoted piece moves
                    pass
                else:
                    # Normal piece moves

                    adjacent_piece = position + i
                    next_adjacent_piece = position + 2 * i
                    
                    if self.is_outside_board(adjacent_piece):
                        continue

                    if self.player_owns_piece(gameboard, player, adjacent_piece) and startPosition is None:
                        # You own the piece, can't move there
                        continue

                    elif self.at(gameboard, adjacent_piece) == Pieces.EMPTY and startPosition is None:
                        # There is an empty piece you can move to
                        piece_legal_moves.append(adjacent_piece)
                        pieces_to_remove.append([])

                        tempgameboard = np.copy(gameboard)

                        self.move_piece(tempgameboard, position, adjacent_piece)
                        self.get_piece_legal_move(
                            player, adjacent_piece,
                            startPosition=position, piece_legal_moves = piece_legal_moves,
                            pieces_to_remove = pieces_to_remove, gameboard=tempgameboard,
                            lastNode=node, movetree=movetree, canMove = False
                        )

                    elif (
                        not self.player_owns_piece(gameboard, player, adjacent_piece) 
                        and self.at(gameboard, adjacent_piece) != Pieces.EMPTY
                        and not self.is_outside_board(next_adjacent_piece)
                        ):

                        if self.at(gameboard, next_adjacent_piece) == Pieces.EMPTY:
                            # Jump possible
                            # Need to branch from here
                            # repeat search for new position = next_adjacent_piece
                            piece_legal_moves.append(next_adjacent_piece)
                            pieces_to_remove.append(adjacent_piece)
                            
                            # need a way to know when a branch has ended
                            # to go back to the last node

                            tempgameboard = np.copy(gameboard)

                            self.remove_piece(tempgameboard, adjacent_piece)
                            self.move_piece(tempgameboard, position, next_adjacent_piece)

                            self.get_piece_legal_move(
                                player, next_adjacent_piece,
                                startPosition=position, piece_legal_moves = piece_legal_moves,
                                pieces_to_remove = pieces_to_remove, gameboard=tempgameboard,
                                lastNode=node, movetree=movetree, canMove = False
                            )
            
        return {
            'legal_moves' : piece_legal_moves,
            'remove' : pieces_to_remove,
            'tree' : movetree
        }


    # def check_win_state(self, Player):
    def check_win_state(self):
        '''
        1. Opponent has no legal moves (all pieces are captured, or completely blocked)
        2. King vs. single man
        '''
        pass
    
    def increment_turn(self):
        self.n_turns += 1