import os
import pickle

import numpy as np

from numba import jit, njit, uint64

from bitOperations import *
from bitboard import *
from bitboard_constants import *
from move import MoveNode, MoveTypes
from attack import get_king_attack, pawnSingleMasks, pawnDoubleMasks
from treelib import Node, Tree

from enum import Enum

# def load_lookup(filePath, fallbackGenerator):
#     if os.path.exists(filePath):
#         return pickle.load(open(filePath, "rb"))
#     else:
#         return fallbackGenerator()

# # Should be in this order, because the later generators depend on the earlier ones
# base = os.path.join(os.path.dirname(__file__), 'lookup')
# blockerMasks    = load_lookup(os.path.join(base, "blockers_mask.pkl")    , _generate_blockers_mask)
# allBlockers     = load_lookup(os.path.join(base, "all_blocker.pkl")      , _generate_all_blockers)
# kingMagicLookup = load_lookup(os.path.join(base, "king_magic_lookup.pkl"), _generate_king_lookup)
# pawnSingleMasks = load_lookup(os.path.join(base, "pawn_single.pkl")      , _generate_pawn_single_moves)
# pawnDoubleMasks = load_lookup(os.path.join(base, "pawn_double.pkl")      , _generate_pawn_jumps)

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
        firstAttackQuery = np.uint64(get_king_attack(pos, board))
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
            landingSpots = np.uint64(get_king_attack(pos, tempBoard)) & ~firstAttackQuery & ~board

        # The case where the attack wasn't valid, but the king can still move
        # Only kings are ever going to reach this point of the logic
        if landingSpots == 0 and canMove and not evaluator.hasEverJumped:
            # print("Only king sliding moves available")
            slide = get_active_indices(get_king_attack(pos, board) & ~board)
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
                        child = MoveNode(moveFrom=pos, moveTo=land, capture=capture, moveType=MoveTypes.JUMP, promotion=False)
                        
                        childBoard = board
                        childOppBoard = oppBoard
                        childMyKing = myKing
                        childMyPawn = myPawn

                        # Remove the captured piece
                        childOppBoard = clear_bit(capture, childOppBoard)
                        childBoard = clear_bit(capture, childBoard)

                        # Move the Piece
                        childBoard = move_piece(pos, land, childBoard)
                        if isPawn:
                            childMyPawn = move_piece(pos, land, childMyPawn)
                        elif isKing:
                            childMyKing = move_piece(pos, land, childMyKing)

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
        if is_piece_present(pos, myPawn):
            slide = get_active_indices(pawnSingleMasks[pos] & ~board)
        elif is_piece_present(pos, myKing):
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

def evaluate(boardClass:BoardParent):
    moveTreeList = []
    evaluator = Evaluator()
    maxDepth = 0

    indices = get_active_indices(boardClass.myPawn)
    indices.extend(get_active_indices(boardClass.myKing))

    # Could split indices into equally sized lists and run threaded

    for pos in indices:
        tree = get_all_generalized_moves(
            pos, boardClass.board, boardClass.myPawn, boardClass.myKing, boardClass.oppBoard, evaluator=evaluator
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


    # A lot of the pruning can be simplified by expanding on the evaluator class
    # Should keep track if each tree has jumped AND the depth of each tree
    # 
    # If any tree jumped, remove the ones that didn't
    # 
    # For every short tree added before the longest one, delete the short ones
    # 
    # Finally combine them all in one big tree

    m = max(evaluator.depthTracker)
    remove = sorted([i for i, j in enumerate(evaluator.depthTracker) if j!=m], reverse=True)

    for i in remove:
        del moveTreeList[i]
        del evaluator.jumpTracker[i]
    
    if evaluator.hasEverJumped:
        remove = sorted([i for i in enumerate(evaluator.jumpTracker) if i==False])
        for i in remove:
            del moveTreeList[i]

    tree = Tree()
    rootMove = MoveNode(moveFrom=None, moveTo=None, moveType=MoveTypes.START)
    rootNode = Node(tag=rootMove.tag, data=rootMove)
    tree.add_node(rootNode)
    
    for movetree in moveTreeList:
        tree.paste(rootNode.identifier, movetree)

    return tree

def getValidBranch(tree):
    # Prune the tree to keep the longest branches
    
    def remove_nodes_list(t, remove):
        for nodeID in remove:
            if t.contains(nodeID):
                t.remove_node(nodeID)

    maxDepth = tree.depth()

    nodesToRemove = []

    containsJump = False

    for leaf in tree.leaves():
        for nodeID in tree.rsearch(leaf.identifier):
            # print(tree.get_node(nodeID).tag)

            if ((tree.depth(nodeID) < maxDepth) and tree.children(nodeID) == []) or (tree.depth(nodeID) == 1 and tree.children(nodeID) == []):
                # print("\tPRUNE: {}".format(tree.get_node(nodeID).tag))
                nodesToRemove.append(nodeID)

            if maxDepth == 2 and tree.get_node(nodeID).data.moveType == MoveTypes.JUMP:
                containsJump = True
            # print()

    remove_nodes_list(tree, nodesToRemove)

    # If depth is 2, then iterate thru the tree to see if there is a jump
    # If yes, then remove the quiet moves
    nodesToRemove = []
    if containsJump:
        for leaf in tree.leaves():
            for nodeID in tree.rsearch(leaf.identifier):
                if tree.get_node(nodeID).data.moveType == MoveTypes.QUIET:
                    nodesToRemove.append(nodeID)
                    nodesToRemove.append(tree.parent(nodeID).identifier)
    
    remove_nodes_list(tree, nodesToRemove)

    # This is to remove the moves that used to have children, but now don't
    # Example: for the PawnJumps board.
    # There must be a better way to prune :/
    nodesToRemove = []
    for leaf in tree.leaves():
        for nodeID in tree.rsearch(leaf.identifier):
            if ((tree.depth(nodeID) < maxDepth) and tree.children(nodeID) == []):
                nodesToRemove.append(nodeID)
    
    remove_nodes_list(tree, nodesToRemove)

    return tree

def listFromTree(tree):
    moveList = [path[2:] for path in tree.paths_to_leaves()]
    for i in range(0, len(moveList)):
        for j in range(0, len(moveList[i])):
            moveList[i][j] = tree.get_node(moveList[i][j]).data
    return moveList

if __name__ == '__main__':
    import time

    # ################################################
    # Evaluate the Generalized Routine

    # boards = [StartingBoard, PawnJumps, KingJumps, PawnPromote]
    boards = [StartingBoard]

    for b in boards:
        print(b.tag)
        
        time1 = time.time()
        tree = evaluate(b)
        time2 = time.time()
        getValidBranch(tree)
        moveList = listFromTree(tree)
        time3 = time.time()

        print("Generated the tree in: {}us".format(1000000*(time2-time1)))
        print("Validated the tree in: {}us".format(1000000*(time3-time2)))
        print()

        # tree.show()

        # for move in moveList:
        #     myPawn1, myKing1, oppPawn1, oppKing1 = perform_move(move, b.myPawn, b.myKing, b.oppPawn, b.oppKing)
        #     print_bitboard([ myPawn1, myKing1, oppPawn1, oppKing1 ])
        #     print()

    def timethis(n, board):
        """ Returns the individual time for each run in ms
        """
        cumTime = 0
        for i in range(0, n):
            time1 = time.time()
            getValidBranch(evaluate(board))
            time2 = time.time()
            cumTime += (time2 - time1)
        
        cumTime *= 1000
        
        return cumTime / n

    print(timethis(1000, StartingBoard))

    # Starting board ~1.3ms
    # Pawn promote ~0.7ms
    # King jumps ~0.9ms
    # Pawn jumps ~0.7ms
    # King zigzag ~
