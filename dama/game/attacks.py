import os
import pickle

import numpy as np

from bitOperations import *
from bitboard import *
from bitboard_constants import *
from move import MoveNode, MoveTypes

from treelib import Node, Tree

from enum import Enum

# Magic bitboards
# ~~~~spooky

# A couple constants
_rookMagics = np.array([
    0xa8002c000108020, 0x6c00049b0002001, 0x100200010090040, 0x2480041000800801, 0x280028004000800,
    0x900410008040022, 0x280020001001080, 0x2880002041000080, 0xa000800080400034, 0x4808020004000,
    0x2290802004801000, 0x411000d00100020, 0x402800800040080, 0xb000401004208, 0x2409000100040200,
    0x1002100004082, 0x22878001e24000, 0x1090810021004010, 0x801030040200012, 0x500808008001000,
    0xa08018014000880, 0x8000808004000200, 0x201008080010200, 0x801020000441091, 0x800080204005,
    0x1040200040100048, 0x120200402082, 0xd14880480100080, 0x12040280080080, 0x100040080020080,
    0x9020010080800200, 0x813241200148449, 0x491604001800080, 0x100401000402001, 0x4820010021001040,
    0x400402202000812, 0x209009005000802, 0x810800601800400, 0x4301083214000150, 0x204026458e001401,
    0x40204000808000, 0x8001008040010020, 0x8410820820420010, 0x1003001000090020, 0x804040008008080,
    0x12000810020004, 0x1000100200040208, 0x430000a044020001, 0x280009023410300, 0xe0100040002240,
    0x200100401700, 0x2244100408008080, 0x8000400801980, 0x2000810040200, 0x8010100228810400,
    0x2000009044210200, 0x4080008040102101, 0x40002080411d01, 0x2005524060000901, 0x502001008400422,
    0x489a000810200402, 0x1004400080a13, 0x4000011008020084, 0x26002114058042
], dtype=np.uint64)

_rookIndexBits = np.array([
    12, 11, 11, 11, 11, 11, 11, 12,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12
], dtype=np.uint64)

def load_lookup(filePath, fallbackGenerator):
    if os.path.exists(filePath):
        return pickle.load(open(filePath, "rb"))
    else:
        return fallbackGenerator()

def _generate_king_masks(pos):
    row, col = get_row_col(pos)
    masks = (rowMask[row] | colMask[col]) & ~single(row, 0) & ~single(row, 7) & ~single(0, col) & ~single(7, col) & ~single(row, col)
    return masks

def _generate_blockers_mask():
    blockerMasks = np.zeros(64, dtype=np.uint64)
    for i in range(0, 64):
        blockerMasks[i] = _generate_king_masks(i)
    return blockerMasks

def _generate_single_blocker(index, pos, mask):
    blocker = np.uint64(0)
    index = (bin(index)[2:]).zfill(_rookIndexBits[pos])

    for i in range(0, popCount(mask)):
        lsb = bitScanForward(mask)
        mask = mask & ~single(lsb)
        row, col = get_row_col(lsb)

        value = np.uint64(index[i])
        blocker = set_cell_value(blocker, row, col, value)

    return blocker

def _generate_all_blockers():
    allBlockers = np.zeros(shape=(64, 4096), dtype=np.uint64)

    for i in range(0, 64):
        n = np.power(np.uint64(2), _rookIndexBits[i])
        for j in range(0, n):
            allBlockers[i][j] = _generate_single_blocker(j, i, blockerMasks[i])

    return allBlockers

# Calculate the keys and attack results for each board
def _generate_king_lookup():
    kingMagicLookup = np.zeros(shape=(64, 4096), dtype=np.uint64)

    for i in range(0, 64):
        n = np.power(np.uint64(2), _rookIndexBits[i])

        for j in range(0, n):
            blockers = allBlockers[i][j]
            key = (blockers * _rookMagics[i]) >> (np.uint64(64) - _rookIndexBits[i])
            kingMagicLookup[i][key] = HAndVMoves(i, blockers)

    return kingMagicLookup

# I can save this to a file for reusability, but it doesnt take
# that long to compute
def _generate_pawn_single_moves():
    moves = []
    for i in reversed(range(0, 8)):
        for j in range(0, 8):
            board = np.zeros(shape=[8,8], dtype=np.uint8)
            if j-1 >= 0:
                board[i][j-1] = 1
            if j+1 <= 7:
                board[i][j+1] = 1
            if i-1 >= 0:
                board[i-1][j] = 1
            moves.append(array2bit(board))
    return moves

def _generate_pawn_jumps():
    moves = []
    for i in reversed(range(0, 8)):
        for j in range(0, 8):
            board = np.zeros(shape=[8,8], dtype=np.uint8)
            if j-2 >= 0:
                board[i][j-2] = 1
            if j+2 <= 7:
                board[i][j+2] = 1
            if i-2 >= 0:
                board[i-2][j] = 1
            moves.append(array2bit(board))    
    return moves    

# Finally, get the attack with this function
def get_king_attack(pos:int, board:int) -> int:
    board &= blockerMasks[pos]
    key = (board * _rookMagics[pos]) >> (np.uint64(64) - _rookIndexBits[pos])
    return kingMagicLookup[pos][key]

def HAndVMoves(s:int, board:int) -> int:
    binaryS = np.uint64(1) << np.uint64(s)
    row, col = get_row_col(s)
    
    possibilitiesHorizontal = (board - (np.uint64(2) * binaryS)) ^ reverse64(reverse64(board) - (np.uint64(2) * reverse64(binaryS)))
    possibilitiesVertical = ((board&colMask[col]) - (np.uint64(2) * binaryS)) ^ reverse64(reverse64(board&colMask[col]) - (np.uint64(2) * reverse64(binaryS)))

    return (possibilitiesHorizontal&rowMask[row]) | (possibilitiesVertical&colMask[col])

# Should be in this order, because the later generators depend on the earlier ones
base = os.path.join(os.path.dirname(__file__), 'lookup')
blockerMasks    = load_lookup(os.path.join(base, "blockers_mask.pkl")    , _generate_blockers_mask)
allBlockers     = load_lookup(os.path.join(base, "all_blocker.pkl")      , _generate_all_blockers)
kingMagicLookup = load_lookup(os.path.join(base, "king_magic_lookup.pkl"), _generate_king_lookup)
pawnSingleMasks = load_lookup(os.path.join(base, "pawn_single.pkl")      , _generate_pawn_single_moves)
pawnDoubleMasks = load_lookup(os.path.join(base, "pawn_double.pkl")      , _generate_pawn_jumps)

def decompose_directions(pos, board):
    masks = get_ray_masks(pos)
    decomposed_board = []

    for m in masks:
        decomposed_board.append(board & m)

    return decomposed_board


def get_all_king_moves(pos, board, myPawn, oppBoard, canMove = True, parentNode = None, moveTree = None):

    if moveTree is None:        
        moveTree = Tree()
        parentMove = MoveNode()
        parentNode = Node(tag = parentMove.tag, data=parentMove)
        moveTree.add_node(parentNode)

    attacks = get_king_attack(pos, board) & ~myPawn

    # moveTree.show()
    
    if (attacks & oppBoard):
        # Potentially an enemy being attacked. Let's run this again to make sure

        # Remove the opp pieces that are being attacked
        tempBoard = board & ~(attacks & oppBoard)

        # Run again
        attacks2 = get_king_attack(pos, tempBoard) & ~myPawn
        landingSpots = attacks2 & ~attacks & ~oppBoard

        # print_bitboard([ board, attacks, tempBoard, attacks2, landingSpots])

        # Only sliding moves available
        if landingSpots == 0 and canMove:
            # return the sliding moves
            print("Only sliding moves available")
            # if hasnt jumped yet, return sliding moves
            # else these moves arent valid
            slide = get_active_indices(attacks & empty)
            for i in slide:
                child = MoveNode(i, None)
                childNode = Node(tag=child.tag, data=child)
                moveTree.add_node(childNode, parentNode)

        else:
            # print("Attacks available")
            attack_dir = decompose_directions(pos, attacks & oppBoard)
            landing_dir = decompose_directions(pos, landingSpots)

            for a, l in zip(attack_dir, landing_dir):
                potentialCapture = get_active_indices(a)

                if len(potentialCapture) > 0:
                    capture = potentialCapture[0]
                    l_indices = get_active_indices(l)
                    
                    for land in l_indices:
                        child = MoveNode(land, capture)
                        childNode = Node(tag=child.tag, data=child)
                        moveTree.add_node(childNode, parentNode)
                        

                        childBoard = board
                        childOppBoard = oppBoard

                        # Remove the captured piece
                        childOppBoard = clear_bit(capture, childOppBoard)

                        # Maybe there's a way to update the board
                        # based on what oppBoard is. Instead of applying the
                        # same operation twice?
                        childBoard = clear_bit(capture, childBoard)

                        # Move the king
                        childBoard = move_piece(pos, land, childBoard)

                        # print("Parent: {} and Child: {}".format(parentNode.tag, childNode.tag))
                        # print_bitboard([ board, childBoard ])
                        # print()

                        get_all_king_moves(land, childBoard, myPawn, childOppBoard, canMove = False, parentNode = childNode, moveTree=moveTree)

    else:
        # End of branch
        pass

    return moveTree

# To speed up computation for the game move generation:
# if get_all_pawn_moves returns a jump, then call get_all_king_moves(canMove=False)
# to ignore the sliding move generation. They will be pruned out anyway since there is a mandatory
# pawn jump, so might as well ignore them. 
# 
# Also calculate the pawn moves first since skipping the evaluating the 
# king slides would be time consuming. Or maybe since there are more pawns it'll take more
# time? Idk should experiment with it
def get_all_pawn_moves(pos, board, myPawn, oppBoard, canMove = True, parentNode = None, moveTree = None):

    if moveTree is None:        
        moveTree = Tree()
        parentMove = MoveNode()
        parentNode = Node(tag = parentMove.tag, data=parentMove)
        moveTree.add_node(parentNode)

    attacks = pawnSingleMasks[pos] & oppBoard

    # moveTree.show()
    
    if (attacks):
        # Potentially an enemy being attacked. Let's run this again to make sure

        # Remove the opp pieces that are being attacked
        tempBoard = board & ~(attacks)

        # Run again
        landingSpots = pawnDoubleMasks[pos] & ~board

        # print_bitboard([ board, attacks, tempBoard, attacks2, landingSpots])

        if landingSpots != 0:
            # print("Attacks available")
            attack_dir = decompose_directions(pos, attacks)
            landing_dir = decompose_directions(pos, landingSpots)

            for a, l in zip(attack_dir, landing_dir):
                potentialCapture = get_active_indices(a)

                if len(potentialCapture) > 0:
                    capture = potentialCapture[0]
                    l_indices = get_active_indices(l)
                    
                    for land in l_indices:
                        child = MoveNode(land, capture)
                        childNode = Node(tag=child.tag, data=child)
                        moveTree.add_node(childNode, parentNode)
                        
                        childBoard = board
                        childOppBoard = oppBoard

                        # Remove the captured piece
                        childOppBoard = clear_bit(capture, childOppBoard)

                        # Maybe there's a way to update the board
                        # based on what oppBoard is. Instead of applying the
                        # same operation twice?
                        childBoard = clear_bit(capture, childBoard)

                        # Move the king
                        childBoard = move_piece(pos, land, childBoard)

                        # print("Parent: {} and Child: {}".format(parentNode.tag, childNode.tag))
                        # print_bitboard([ board, childBoard ])
                        # print()

                        get_all_pawn_moves(land, childBoard, myPawn, childOppBoard, canMove = False, parentNode = childNode, moveTree=moveTree)

    if attacks == 0 and canMove:
        # print("No attacks")
        potentialSlides = ~board & pawnSingleMasks[pos]

        if potentialSlides != 0:
            # return the sliding moves
            # print("Only sliding moves available")

            # if hasnt jumped yet, return sliding moves
            # else these moves arent valid
            slide = get_active_indices(potentialSlides)
            for i in slide:
                child = MoveNode(i, None)
                childNode = Node(tag=child.tag, data=child)
                moveTree.add_node(childNode, parentNode)
        else:
            # print("No moves available")
            pass

    return moveTree

def get_all_generalized_moves(pos, board, myPawn, myKing, oppBoard, canMove = True, parentNode = None, moveTree = None, evaluator=None):

    # Initialize the move tree
    if moveTree is None and parentNode is None:
        moveTree = Tree()
        parentMove = MoveNode(moveFrom=pos, moveType=MoveTypes.START)
        parentNode = Node(tag=parentMove.tag, data=parentMove)
        moveTree.add_node(parentNode)
    if evaluator is None:
        evaluator = Evaluator()

    # Could also only evaluate 1 of them. If there's a collision on the boards
    # then I've got a bigger problem
    isKing = is_piece_present(pos, myKing)
    isPawn = is_piece_present(pos, myPawn)

    attacks = np.uint64(0)
    firstAttackQuery = np.uint64(0)
    if isPawn:
        attacks = pawnSingleMasks[pos] & oppBoard
    elif isKing:
        firstAttackQuery = get_king_attack(pos, board)
        attacks = firstAttackQuery & oppBoard

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
            landingSpots = get_king_attack(pos, tempBoard) & ~firstAttackQuery & ~board

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
            attack_dir = decompose_directions(pos, attacks)
            landing_dir = decompose_directions(pos, landingSpots)

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

    print(timethis(10, KingZigzag))

    # Starting board ~1.3ms
    # Pawn promote ~0.7ms
    # King jumps ~0.9ms
    # Pawn jumps ~0.7ms
    # King zigzag ~
