import multiprocessing
import os
import pickle
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List

import numpy as np
from joblib import Parallel, delayed
from numba import jit, njit, uint64
from treelib import Node, Tree

from dama.game.attack import (blockerMasks, get_king_attack, kingMagicLookup,
                              pawnDoubleMasks, pawnSingleMasks)
from dama.game.bitboard import *
from dama.game.bitboard import Bitboard
from dama.game.bitboard_constants import *
from dama.game.bitOperations import *
from dama.game.move import MoveNode, MoveTypes


def decompose_directions(pos, board, mask):
    masks = mask[pos]
    decomposed_board = []

    for m in masks:
        decomposed_board.append(board & np.uint64(m))

    return decomposed_board

def get_all_generalized_moves(pos, board, myPawn, myKing, oppBoard, canMove = True, parentNode = None, moveTree = None, evaluator=None):

    # Initialize the move tree
    if moveTree is None and parentNode is None:
        moveTree = Tree()
        parentMove = MoveNode(moveFrom=pos, moveType=MoveTypes.START)
        parentNode = Node(tag=parentMove.tag, data=parentMove)
        moveTree.add_node(parentNode)
    if evaluator is None:
        evaluator = Evaluator()

    board = np.uint64(board)
    oppBoard = np.uint64(oppBoard)

    # Could also only evaluate 1 of them. If there's a collision on the boards
    # then I've got a bigger problem
    isKing = is_piece_present(pos, myKing)
    isPawn = is_piece_present(pos, myPawn)

    attacks = np.uint64(0)
    firstAttackQuery = np.uint64(0)

    if isPawn:
        attacks = pawnSingleMasks[pos] & oppBoard
    elif isKing:
        firstAttackQuery = np.uint64(get_king_attack(pos, board, blockerMasks, kingMagicLookup))
        attacks = firstAttackQuery & np.uint64(oppBoard)

    if (attacks):
        # Potentially an enemy being attacked. Let's run this again to make sure

        landingSpots = np.uint64(0)
        if isPawn:
            # The square where the pawn would land
            landingSpots = pawnDoubleMasks[pos] & ~board

        elif isKing:
            # Remove the opp pieces that are being attacked
            tempBoard = board & ~attacks
            # Run again
            landingSpots = np.uint64(get_king_attack(pos, tempBoard, blockerMasks, kingMagicLookup)) & ~firstAttackQuery & ~board

        # The case where the attack wasn't valid, but the king can still move
        # Only kings are ever going to reach this point of the logic
        if landingSpots == 0 and canMove and not evaluator.hasEverJumped:
            # print("Only king sliding moves available")
            slide = get_active_indices(np.uint64(get_king_attack(pos, board, blockerMasks, kingMagicLookup)) & ~board)
            for i in slide:
                child = MoveNode(moveFrom=pos, moveTo=i, capture=None, moveType=MoveTypes.QUIET, promotion=False)
                childNode = Node(tag=child.tag, data=child)
                moveTree.add_node(childNode, parentNode)

        else:
            # print("Attacks available")
            attack_dir = decompose_directions(pos, attacks, rayMasks)
            landing_dir = decompose_directions(pos, landingSpots, rayMasks)

            for a, l in zip(attack_dir, landing_dir):
                potentialCapture = get_active_indices(a)

                if len(potentialCapture) > 0:
                    capture = potentialCapture[0]
                    l_indices = get_active_indices(l)
                    
                    for land in l_indices:
                        evaluator.jumped()
                        child = MoveNode(
                            moveFrom=pos, moveTo=land, capture=capture, moveType=MoveTypes.JUMP, promotion=False
                        )
                              
                        childMyPawn, childMyKing, childOppPawn, childOppKing = perform_move(
                            [child], myPawn, myKing, oppBoard, 0
                        )
                        childOppBoard = childOppPawn
                        childBoard = childMyPawn | childMyKing | childOppBoard

                        isPromoted, promotePos = check_promotions(childMyPawn)
                        if isPromoted:
                            # print("PROMOTED")
                            child.promotion = True
                            childMyPawn, childMyKing = promote(promotePos, childMyPawn, childMyKing)
                            # the board overall doesn't change so no need to update

                        childNode = Node(tag=child.tag, data=child)
                        moveTree.add_node(childNode, parent=parentNode)

                        get_all_generalized_moves(
                            land, childBoard, childMyPawn, childMyKing, childOppBoard,
                            canMove = False, parentNode = childNode, moveTree=moveTree, evaluator=evaluator
                        )

    elif attacks == 0 and canMove and not evaluator.hasEverJumped:
        # No attacks availalbe, can only move
        if isPawn:
            slide = get_active_indices(pawnSingleMasks[pos] & ~board)
        elif isKing:
            slide = get_active_indices(attacks & ~board)

        for i in slide:
            childMove = MoveNode(moveFrom=pos, moveTo=i, capture=None, moveType=MoveTypes.QUIET, promotion=False)
            childNode = Node(tag=childMove.tag, data=childMove)
            moveTree.add_node(childNode, parent=parentNode)

    return moveTree

class Evaluator:
    def __init__(self):
        self.hasJumped = False
        self.hasEverJumped = False
        self.depthTracker = []
        self.jumpTracker = []
    def jumped(self):
        self.hasJumped = True
        self.hasEverJumped = True
    def resetJump(self):
        self.hasJumped = False
    def trackDepth(self, depth):
        self.depthTracker.append(depth)
    def trackJump(self, hasJumped):
        self.jumpTracker.append(hasJumped)

def evaluate(board, myPawn, myKing, oppBoard):
    evaluator = Evaluator()
    maxDepth = 0

    indices = get_active_indices(myPawn)
    indices.extend(get_active_indices(myKing))
    moveTreeList = []

    # Could split indices into equally sized lists and run threaded
    # TODO: fix all the functions so they can be compiled. ie do not rely on global variables
    # instead pass the globals in as function parameters
    # Then fix up get_all_generalized_moves() so each run is independent of each other. which means
    # removing the evaluator object.
    # It'll make the validation step later on more time consuming, but it MIGHT speed up the move generation
    # who knows, guess we'll see
    # Might also be better performance to make each process run evaluate() for each board instead of having
    # each process run get_all_generalized_moves() for each piece
    # Should test both alternatives out

    for i in range(len(indices)):
        tree = get_all_generalized_moves(
            indices[i], board, myPawn, myKing, oppBoard, evaluator=evaluator
        )

        currentDepth = tree.depth()

        if currentDepth >= maxDepth:
            maxDepth = currentDepth
            moveTreeList.append(tree)
            
            # Only track the moves that get appended
            evaluator.trackJump(evaluator.hasJumped)
            evaluator.trackDepth(currentDepth)
        
        # Reset all the time between pieces
        evaluator.resetJump()

    if len(evaluator.depthTracker) > 0:
        m = max(evaluator.depthTracker)
        remove = sorted([i for i, j in enumerate(evaluator.depthTracker) if j!=m], reverse=True)

        # For every short tree added before the longest one, delete the short ones
        for i in remove:
            del moveTreeList[i]
            del evaluator.jumpTracker[i]
        
        # If any tree jumped, remove the ones that didn't
        if evaluator.hasEverJumped:
            remove = sorted([i for i in enumerate(evaluator.jumpTracker) if i==False], reverse=True)
            for i in remove:
                del moveTreeList[i]

    # Finally combine them all in one big tree
    tree = Tree()
    rootMove = MoveNode(moveFrom=None, moveTo=None, moveType=MoveTypes.START)
    rootNode = Node(tag=rootMove.tag, data=rootMove)
    tree.add_node(rootNode)
    
    for movetree in moveTreeList:
        tree.paste(rootNode.identifier, movetree)

    # More validation    
    def remove_nodes_list(t, remove):
        for nodeID in remove:
            if t.contains(nodeID):
                t.remove_node(nodeID)

    # If depth is 2, then iterate thru the tree to see if there is a jump
    # If yes, then remove the quiet moves
    # This is to remove the moves that used to have children, but now don't
    # Example: for the PawnJumps board.
    # There must be a better way to prune :/
    nodesToRemove = []
    for leaf in tree.leaves():
        for nodeID in tree.rsearch(leaf.identifier):
            alreadyAppended = False

            if evaluator.hasEverJumped and tree.get_node(nodeID).data.moveType == MoveTypes.QUIET:
                if tree.get_node(nodeID).data.moveType == MoveTypes.QUIET:
                    nodesToRemove.append(nodeID)
                    nodesToRemove.append(tree.parent(nodeID).identifier)
                    alreadyAppended = True

            if ((tree.depth(nodeID) < maxDepth) and tree.children(nodeID) == []) and not alreadyAppended:
                nodesToRemove.append(nodeID)
    
    remove_nodes_list(tree, nodesToRemove)

    return tree

def listFromTree(tree):
    moveList = [path[2:] for path in tree.paths_to_leaves()]
    for i in range(0, len(moveList)):
        for j in range(0, len(moveList[i])):
            moveList[i][j] = tree.get_node(moveList[i][j]).data
    return moveList

def get_all_legal_moves_list(currentBoard:Bitboard):
    return listFromTree(evaluate(currentBoard.board, currentBoard.myPawn, currentBoard.myKing, currentBoard.oppBoard))

def get_moves_from_tree(tree):
    ''' Assumes move_search(board, depth=0)
    '''
    movelist = []
    for node in tree.all_nodes_itr():
        movelist.append(node.data.moveList)

    movelist.pop(0)

    return movelist

@dataclass
class MoveSearchNode:
    bitboards : Bitboard
    moveList : List[MoveNode]
    activePlayer : bool

def move_search(currentBoard, depth, forceParallel=False):
    assert depth >= 0 and depth <= 5
    # Initialize the master tree by doing a 0-depth move search
    tree = move_search_single(currentBoard, 0)
    
    if depth == 0:
        return tree

    branchIDs = []
    sub_boards = []

    for node in tree.leaves():
        branchIDs.append(node.identifier)
        sub_boards.append(
            flip_color(tree.get_node(node.identifier).data.bitboards)
        )

    n_cpus = 1
    if forceParallel or depth >= 4:
        n_cpus = multiprocessing.cpu_count()

    # print("Running on {} cpus".format(n_cpus))

    results = Parallel(n_jobs=n_cpus, backend="multiprocessing")(
        delayed(move_search_single)(sub_boards[i], depth - 1) for i in range(0, len(sub_boards))
    )

    for i in range(0, len(branchIDs)):
        tree.paste(branchIDs[i], results[i])
        tree.link_past_node(results[i].root)

    return tree

def move_search_single(
    currentBoard:Bitboard, depth, activePlayer = True, 
    tree = None, parentNode = None, debug=True
    ):

    # Flip board between moves, but not for the first time
    if tree is not None:
        currentBoard = flip_color(currentBoard)

    if tree is None:
        tree = Tree()
        parentMoveSearchNode = MoveSearchNode(bitboards=currentBoard, moveList=[], activePlayer=activePlayer)
        parentNode = Node(data=parentMoveSearchNode)
        tree.add_node(parentNode)

    moveList = get_all_legal_moves_list(currentBoard)

    for move in moveList:
        
        if debug:
            n_jumps = 0
            n_promotions = 0
            for m in move:
                if m.moveType == MoveTypes.JUMP:
                    n_jumps += 1
                if m.promotion:
                    n_promotions += 1

        childBoard = perform_move_board(move, currentBoard)

        if debug:
            assert popCount(childBoard.board) == (popCount(currentBoard.board) - n_jumps)
            assert n_promotions == 1 or n_promotions == 0
            assert popCount(childBoard.myKing) == (popCount(currentBoard.myKing) + n_promotions)

        childState = MoveSearchNode(bitboards=childBoard, moveList=move, activePlayer=not activePlayer)
        childNode = Node(data=childState, identifier=uuid.uuid4().hex)
        tree.add_node(childNode, parent=parentNode)

        if depth is not 0:
            move_search_single(
                childBoard, depth - 1, activePlayer = not activePlayer,
                tree = tree, parentNode = childNode
            )

    return tree

def test_bitboard_contants():
    boards = [StartingBoard, PawnJumps, KingJumps, PawnPromote]

    for b in boards:
        print(b.tag)
        tree = evaluate(b.board, b.myPawn, b.myKing, b.oppBoard)
        time1 = time.time()
        tree = evaluate(b.board, b.myPawn, b.myKing, b.oppBoard)
        time2 = time.time()
        moveList = listFromTree(tree)
        time3 = time.time()

        print("Generated the tree in: {}us".format(1000000*(time2-time1)))
        print("Got moves in         : {}us".format(1000000*(time3-time2)))
        print()

        # tree.show()

        # for move in moveList:
        #     myPawn1, myKing1, oppPawn1, oppKing1 = perform_move(move, b.myPawn, b.myKing, b.oppPawn, b.oppKing)
        #     print_bitboard([ myPawn1, myKing1, oppPawn1, oppKing1 ])
        #     print()

def test_flipping_color(board):
    print_bitboard([ board.board, board.myPawn, board.oppPawn ])
    print()

    # white moves
    white_tree = evaluate(board.board, board.myPawn, board.myKing, board.oppBoard)
    white_moves = listFromTree(white_tree)
    board = perform_move_board(white_moves[0], board)
    print_bitboard([ board.board, board.myPawn, board.oppPawn ])
    print()

    # black moves
    board = flip_color(board)
    black_tree = evaluate(board.board, board.myPawn, board.myKing, board.oppBoard)
    black_moves = listFromTree(black_tree)
    board = perform_move_board(black_moves[0], board)
    print_bitboard([ board.board, board.myPawn, board.oppPawn ])
    print()

    #  white again
    board = flip_color(board)
    print_bitboard([ board.board, board.myPawn, board.oppPawn ])
    print()
    white_tree = evaluate(board.board, board.myPawn, board.myKing, board.oppBoard)
