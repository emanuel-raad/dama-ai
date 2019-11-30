import numpy as np
from dama.agents.player import Player
from dama.game.constants import Pieces
from dama.game.constants import Color
from dama.game.gameboard import Gameboard

from dama.game import direction
from treelib import Node, Tree

class State(object):
    '''
    Class to store the representation of the game at each
    node of the tree.

    Contains the gameboard, the position of the piece that just moved

    Tag is a string representation of the position
    '''
    def __init__(self, gameboard, position):
        self.gameboard = gameboard
        self.position = position
        self.tag = np.array2string(position)

class DamaGame:
    def __init__(self, board=None):
        self.n_turns = 0
        self.gameboard = Gameboard(gameboard = board)

    def get_all_legal_moves(self, gameboard, player):
        
        legal_moves = []

        for x in range(0, self.gameboard.rows):
            for y in range(0, self.gameboard.cols):
                if self.gameboard.player_owns_piece(player, [x, y]):
                    pass
                else:
                    pass

        return legal_moves

    def get_piece_legal_move(
        self, player, position, startPosition = None,
        pieces_to_remove = None, current_gameboard = None,
        movetree = None, lastNode = None, canMove = True, hasJumped = False
    ):

        '''
        position is the current position of the piece whose moves we are inspecting

        startPosition is the original position of that move, before any jumps have been made
        '''

        # Initialize empty lists
        if pieces_to_remove is None:
            pieces_to_remove = []
        if current_gameboard is None:
            current_gameboard = self.gameboard

        # Add the node to the movetree, or create one if it doesn't exist
        if movetree is None:
            movetree = Tree()

        if current_gameboard.player_owns_piece(player, position):

            # Create a node for the tree from the current state of the game
            state = State(current_gameboard, position)
            node = Node(tag=state.tag, data=state)

            # if current_gameboard.player_owns_piece(player, position):
            if lastNode is None:
                # Set current node as the root
                movetree.add_node(node)
                lastNode = node
            else:
                # Create a new node as the child of the last node
                movetree.add_node(node, parent=lastNode)

            valid_directions = direction.get_valid_directions(
                startPosition, position, player.color, current_gameboard.is_promoted(position)
            )

            if current_gameboard.is_promoted(position):
                lookup_range = max(current_gameboard.rows, current_gameboard.cols)
            else:
                lookup_range = 3

            for dir in valid_directions:
                
                jumpIsAvailable = False
                jumpablePiece = None

                for multiplier in range(1, lookup_range):

                    if not current_gameboard.is_promoted(position):
                        if multiplier == 2 or hasJumped:
                            canMove = False
                        elif multiplier == 1 and not hasJumped:
                            canMove = True
                    
                    next = position + multiplier * dir
                    next_next = position + (multiplier + 1) * dir

                    # Check for any collision or invalid moves

                    # Out of board
                    # Quit
                    if current_gameboard.is_outside_board(next):
                        break

                    # You own the next piece
                    # Quit
                    elif current_gameboard.player_owns_piece(player, next):
                        break
                    
                    # Collion with two back to back pieces
                    # Quit
                    elif (
                        not current_gameboard.at(next) == Pieces.EMPTY
                        and not current_gameboard.is_outside_board(next_next)
                        and not current_gameboard.at(next_next) == Pieces.EMPTY
                        and not current_gameboard.player_owns_piece(player, next)
                        and not current_gameboard.player_owns_piece(player, next_next)
                    ):
                        break
                    
                    if current_gameboard.at(next) == Pieces.EMPTY:
                        if jumpIsAvailable:
                            if current_gameboard.opponents_between_two_positions(player, position, next) < 2:
                                temp_gameboard = Gameboard(gameboard=np.copy(current_gameboard.gameboard))
                                temp_gameboard.move_piece(position, next)
                                temp_gameboard.remove_piece(jumpablePiece)

                                self.get_piece_legal_move(
                                    player, next, startPosition = position,
                                    pieces_to_remove = None, current_gameboard = temp_gameboard,
                                    movetree = movetree, lastNode = node, canMove = False, hasJumped = True
                                )

                        elif canMove:
                            # gameboard gameboard gameboard
                            temp_gameboard = Gameboard(gameboard=np.copy(current_gameboard.gameboard))
                            temp_gameboard.move_piece(position, next)

                            new_state = State(temp_gameboard, next)
                            new_node = Node(tag=new_state.tag, data=new_state)

                            movetree.add_node(new_node, parent=node)
                    elif (
                        not current_gameboard.at(next) == Pieces.EMPTY
                        and not current_gameboard.player_owns_piece(player, next)
                    ):
                        if not jumpIsAvailable:
                            jumpIsAvailable = True
                            jumpablePiece = next

        return {
            'legal_moves' : [],
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