import numpy as np
import os
from treelib import Node, Tree

from dama.agents.player import Player
from dama.game.constants import Pieces
from dama.game.constants import Color
from dama.game.gameboard import Gameboard
from dama.game import direction

class State(object):
    '''
    Class to store the representation of the game at each
    node of the tree.

    Contains the gameboard, the position of the piece that just moved

    Tag is a string representation of the position
    '''
    def __init__(self, position, removed):
        self.position = position
        self.removed = removed
        self.tag = np.array2string(position)
        if removed is None:
            self.remove_tag = 'None'
        else:
            self.remove_tag = np.array2string(removed)

class DamaGame:
    def __init__(self, board=None):
        self.n_turns = 0
        self.gameboard = Gameboard(gameboard = board)
        self.white_player = None
        self.black_player = None
        self.starting_player_color = None

    def setAgent(self, agent):
        if agent.color == Color.WHITE:
            self.white_player = agent
        elif agent.color == Color.BLACK:
            self.black_player = agent

    def checkAgentStatus(self):
        return self.white_player is not None and self.black_player is not None

    def setStartingPlayer(self, agent):
        self.starting_player_color = agent.color

    def start_game(self):
        if not self.checkAgentStatus():
            print("Error, not all agents are set.")
            return

        running = True

        if self.starting_player_color is None or self.starting_player_color == Color.WHITE:
            agentFlipFlop = True
        else:
            agentFlipFlop = False

        while running:
            if agentFlipFlop:
                current_player = self.white_player
            else:
                current_player = self.black_player

            # Process Events
            self.increment_turn()

            # Draw
            self.gameboard.print_board()
            print("{}'s turn".format(current_player.color))
            print("Turn: {}".format(self.n_turns))
            print()

            # Update
            # Get all posible moves
            res = self.get_all_legal_moves(current_player)
            
            # Check Win State
            metrics = self.gameboard.metrics(current_player)
            if (
                # No moves left
                len(res['move']) == 0 or
                (
                # Little dude vs King
                metrics['myPieces'] == 1
                and metrics['myPromoted'] == 0
                and metrics['opponentPieces'] == 0
                and metrics['opponentPromoted'] == 1
                )
            ):
                running = False
                winner = not agentFlipFlop
                break

            # Ask the player for his choice
            choice = current_player.request_move(self.gameboard, res['move'], res['remove'])
            print("You picked {}".format(choice))

            # Perform the player's move
            self.performMove(res['move'][choice], res['remove'][choice])

            # End turn

            # check win status
            if self.n_turns == 1000:
                running = False
            # check promote status
            self.check_for_promotions()

            # Switch the player
            agentFlipFlop = not agentFlipFlop
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
        
        # Declare the winner
        if winner:
            print("Winner is {}".format(self.white_player.color))
        else:
            print("Winner is {}".format(self.black_player.color))

    def check_for_promotions(self, temp_gameboard=None):
        if temp_gameboard is None:
            gameboard = self.gameboard
        else:
            gameboard = temp_gameboard

        row_index = [0, gameboard.rows - 1]
        for i in row_index:
            for j in range(gameboard.cols):
                pos = np.array([i, j])
                if i == 0:
                    if gameboard.at(pos) == Pieces.BLACK:
                        gameboard.gameboard[i][j] = Pieces.BLACK_PROMOTED
                elif i == gameboard.rows - 1:
                    if gameboard.at(pos) == Pieces.WHITE:
                        gameboard.gameboard[i][j] = Pieces.WHITE_PROMOTED

    def get_all_legal_moves(self, player, temp_gameboard=None):

        if temp_gameboard is None:
            gameboard = self.gameboard
        else:
            gameboard = Gameboard(gameboard=np.copy(temp_gameboard.gameboard))

        all_move_list = []
        all_remove_list = []
        all_count_list = []

        for x in range(0, gameboard.rows):
            for y in range(0, gameboard.cols):
                pos = np.array([x, y])
                if gameboard.player_owns_piece(player, pos):
                    all_possible_move_tree = self.get_piece_legal_move(player, pos, current_gameboard=gameboard)
                    
                    if all_possible_move_tree.depth() > 0:
                        b =  listFromTree(all_possible_move_tree)

                        all_move_list.extend(b['move'])
                        all_remove_list.extend(b['remove'])
                        all_count_list.extend(b['count'])
        
        if len(all_count_list) > 0:    
            max_indices = np.argwhere(all_count_list == np.amax(all_count_list)).flatten().tolist()

            valid_moves = [all_move_list[i] for i in max_indices]
            valid_removes = [all_remove_list[i] for i in max_indices]
            valid_counts = [all_count_list[i] for i in max_indices]

            return {
                'move' : valid_moves,
                'remove' : valid_removes,
                'count' : valid_counts
            }
        else:
            return {
                'move' : [],
                'remove' : [],
                'count' : []
            }

    def get_piece_legal_move(
        self, player, position, startPosition = None,
        current_gameboard = None, lastRemoved = None,
        movetree = None, lastNode = None, canMove = True, hasJumped = False
    ):

        '''
        position is the current position of the piece whose moves we are inspecting

        startPosition is the original position of that move, before any jumps have been made
        '''

        # Initialize empty lists
        if current_gameboard is None:
            current_gameboard = self.gameboard

        # Check for promotions
        self.check_for_promotions(current_gameboard)

        # Add the node to the movetree, or create one if it doesn't exist
        if movetree is None:
            movetree = Tree()

        if current_gameboard.player_owns_piece(player, position):

            # Create a node for the tree from the current state of the game
            state = State(position, lastRemoved)
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
                                    current_gameboard = temp_gameboard, lastRemoved=jumpablePiece,
                                    movetree = movetree, lastNode = node, canMove = False, hasJumped = True
                                )

                        elif canMove:
                            # gameboard gameboard gameboard
                            temp_gameboard = Gameboard(gameboard=np.copy(current_gameboard.gameboard))
                            temp_gameboard.move_piece(position, next)

                            new_state = State(next, None)
                            new_node = Node(tag=new_state.tag, data=new_state)

                            movetree.add_node(new_node, parent=node)
                    elif (
                        not current_gameboard.at(next) == Pieces.EMPTY
                        and not current_gameboard.player_owns_piece(player, next)
                    ):
                        if not jumpIsAvailable:
                            jumpIsAvailable = True
                            jumpablePiece = next

                # remove list
                # move list


        return movetree

    # def check_win_state(self, Player):
    def check_win_state(self):
        '''
        1. Opponent has no legal moves (all pieces are captured, or completely blocked)
        2. King vs. single man
        '''
        pass
    
    def increment_turn(self):
        self.n_turns += 1

    def performMove(self, moveList, removeList, temp_gameboard=None):

        if temp_gameboard is None:
            gameboard = self.gameboard
        else:
            # gameboard = Gameboard(gameboard=np.copy(self.gameboard.gameboard))
            gameboard = temp_gameboard

        for i in range(len(moveList)):
            if i == 0:
                pass
            else:
                gameboard.move_piece(moveList[i-1], moveList[i])
                if removeList[i] is not None:
                    gameboard.remove_piece(removeList[i])

    # Kind of obsolete
    def getMetricsAfterMove(self, player, moveList, removeList):
        temp_gameboard = Gameboard(gameboard=np.copy(self.gameboard.gameboard))

        for i in range(len(moveList)):
            if i == 0:
                pass
            else:
                temp_gameboard.move_piece(moveList[i-1], moveList[i])
                if removeList[i] is not None:
                    temp_gameboard.remove_piece(removeList[i])

        return temp_gameboard.metrics(player)

def listFromTree(tree):
    tag_paths = []
    remove_paths = []
    count_list = []
    for i in tree.paths_to_leaves():
        path = []
        r = []
        for j in i:
            path.append(tree.get_node(j).data.position)
            r.append(tree.get_node(j).data.removed)

        tag_paths.append(path)
        remove_paths.append(r)
        count_list.append(countRemoves(r))
    
    return {
        'move' : tag_paths,
        'remove' : remove_paths,
        'count' : count_list
    }

def setFromTree(tree):
    tag_paths = []
    remove_paths = []
    for i in tree.paths_to_leaves():
        path = []
        r = []
        for j in i:
            path.append(tree.get_node(j).data.tag)
            r.append(tree.get_node(j).data.remove_tag)

        tag_paths.append(path)
        remove_paths.append(r)
    
    move_set = set(map(tuple, tag_paths))
    remove_set = set(map(tuple, remove_paths))

    return {
        'move' : move_set,
        'remove' : remove_set
    }

def countRemoves(remove_list):
    count = 0
    for i in remove_list:
        if i is not None:
            count = count + 1
    return count