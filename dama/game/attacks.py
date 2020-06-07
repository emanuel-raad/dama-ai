import os
import pickle

import numpy as np

from bitOperations import *
from bitboard import *
from bitboard_constants import BoardParent, StartingBoard, PawnJumps, KingJumps, KingZigzag

from treelib import Node, Tree

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

class MoveNode(object):
    '''
    Class to store the representation of the game at each
    node of the tree.

    Contains the gameboard, the position of the piece that just moved

    Tag is a string representation of the position
    '''
    def __init__(self, moveTo=None, capture=None):
        self.moveTo = moveTo
        self.capture = capture
        self.tag = "({}, {})".format(moveTo, capture)

    def is_empty(self):
        return self.moveTo is None and self.capture is None


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


# Need to take promotions into account
# A pawn could move to the eigth row and become a king. Then the move generation rules change
# Consider generalizing this function, and applying the appropriate move generation
# depending on the piece type of pos.
# A lot of the code is repeated anyway:
# 
# Query my bitboards (myPawn, myKing) to check if 'pos' is a king or pawn:
# if king                 -> do king move gen
# if pawn, and at 8th row -> promote to king, do king move gen
# if pawn                 -> do pawn move gen
# 
# Best approach (but a lot of work) would be to generate magic bitboards for the pawns as well
# Then just pass the appropriate lookup table to the func
#
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



def get_all_generalized_moves(pos, board, myPawn, myKing, oppBoard, canMove = True, parentNode = None, moveTree = None):

    # Initialize the move tree
    if moveTree is None and parentNode is None:        
        moveTree = Tree()
        parentMove = MoveNode(moveTo=pos)
        parentNode = Node(tag=parentMove.tag, data=parentMove)
        moveTree.add_node(parentNode)

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

        # print("Attacks2 and landing spots")
        # print_bitboard([ attacks2, landingSpots])

        # print_bitboard([ board, attacks, tempBoard, attacks2, landingSpots])

        # The case where the attack wasn't valid, but the king can still move
        # Only kings are every going to reach this point of the logic
        if landingSpots == 0 and canMove:
            # print("Only king sliding moves available")
            slide = get_active_indices(get_king_attack(pos, board) & ~board)
            for i in slide:
                child = MoveNode(i, None)
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
                        child = MoveNode(land, capture)
                        childNode = Node(tag=child.tag, data=child)
                        moveTree.add_node(childNode, parent=parentNode)
                        
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

                        # Should check for promotions here, after moving the piece
                        # And apply them appropriately so that the next loop
                        # Takes it into account

                        get_all_generalized_moves(
                            land, childBoard, childMyPawn, childMyKing, childOppBoard,
                            canMove = False, parentNode = childNode, moveTree=moveTree
                        )

    elif attacks == 0 and canMove:
        # No attacks availalbe, can only move
        slide = np.uint64(0)
        if is_piece_present(pos, myPawn):
            # The square where the pawn would land
            slide = get_active_indices(pawnSingleMasks[pos] & ~board)
        elif is_piece_present(pos, myKing):
            slide = get_active_indices(attacks & ~board)

        # if len(slide) > 0:
            # print("Only slide moves available")
            # print(slide)

        for i in slide:
            childMove = MoveNode(i, None)
            childNode = Node(tag=childMove.tag, data=childMove)
            moveTree.add_node(childNode, parent=parentNode)

    return moveTree


if __name__ == '__main__':
    king = np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ])
    king = array2bit(king)

    # Slides
    # oppBoard = np.array([
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 1, 0, 1, 0, 1, 1, 0],
    #             [1, 0, 0, 0, 0, 0, 0, 1],
    #             [0, 0, 1, 0, 1, 0, 1, 0],
    #             [1, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 1, 0, 1, 0, 1, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 1, 0],
    #             [0, 1, 0, 1, 0, 1, 0, 0]
    #         ])
    # oppBoard = array2bit(oppBoard)

    # Jumps
    oppBoard = np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ])
    oppBoard = array2bit(oppBoard)

    # oppBoard = np.array([
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 1, 0, 0, 0, 0, 0],
    #             [0, 1, 0, 0, 0, 0, 0, 0],
    #         ])
    # oppBoard = array2bit(oppBoard)

    myPawn = np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ])
    myPawn = array2bit(myPawn)


    board = king | oppBoard | myPawn
    empty = ~board
    
    import time
    time1 = time.time()

    # pos = get_active_indices(king)[0]
    # moveTree = get_all_king_moves(pos, board, myPawn, oppBoard)

    # time2 = time.time()
    # print("Completed in {:.4f} ms".format(1000*(time2-time1)))

    # # moveTree.show()
    # # print(moveTree.depth())

    # # Filter for only the longest branches
    # lengths = [len(m) for m in moveTree.paths_to_leaves()]
    # maxLengths = np.argwhere(lengths == np.amax(lengths)).flatten()
    # print("Number of computed paths : {}".format(len(lengths)))
    # print("Number of valid paths    : {}".format(len(maxLengths)))

    # ################################################
    # PAWN

    # pos = get_active_indices(myPawn)[0]
    # moveTree = get_all_pawn_moves(pos, board, myPawn, oppBoard)

    # time2 = time.time()
    # print("Completed in {:.4f} ms".format(1000*(time2-time1)))

    # moveTree.show()
    # # print(moveTree.depth())

    # # Filter for only the longest branches
    # lengths = [len(m) for m in moveTree.paths_to_leaves()]
    # maxLengths = np.argwhere(lengths == np.amax(lengths)).flatten()
    # print("Number of computed paths : {}".format(len(lengths)))
    # print("Number of valid paths    : {}".format(len(maxLengths)))

    # ################################################
    # Starting board moves

    # oppPawn = initialize_board([5, 6])
    # myPawn = initialize_board([1, 2])
    # board = oppPawn | myPawn

    # time1 = time.time()

    # for pos in get_active_indices(myPawn):
    #     moveTree = get_all_pawn_moves(pos, board, myPawn, oppPawn)
    #     # moveTree.show()
    #     # print(moveTree.depth())

    #     # Filter for only the longest branches
    #     # lengths = [len(m) for m in moveTree.paths_to_leaves()]
    #     # maxLengths = np.argwhere(lengths == np.amax(lengths)).flatten()
    #     # print("Number of computed paths : {}".format(len(lengths)))
    #     # print("Number of valid paths    : {}".format(len(maxLengths)))

    # time2 = time.time()
    # print("Completed in {:.4f} ms".format(1000*(time2-time1)))

    # ################################################
    # Generalized Routine

    def evaluate(boardClass:BoardParent, printTree=True, printPaths=False):
        time1 = time.time()

        moveTreeListP = []
        moveTreeListK = []


        for posP in get_active_indices(boardClass.myPawn):
            moveTreeListP.append(
                get_all_generalized_moves(posP, boardClass.board, boardClass.myPawn, boardClass.myKing, boardClass.oppBoard)
            )

        for posK in get_active_indices(boardClass.myKing):
            moveTreeListK.append(
                get_all_generalized_moves(posK, boardClass.board, boardClass.myPawn, boardClass.myKing, boardClass.oppBoard)
            )

        time2 = time.time()
        print("Completed {} in {:.4f} ms".format(boardClass.__name__, 1000*(time2-time1)))

        if printTree or printPaths:
            print("Pawn Info:")
            for m in moveTreeListP:
                if printTree: m.show()

            print("----------")

            print("King Info:")
            for m in moveTreeListK:
                if printTree: m.show()
                if printPaths:
                    lengths = [len(x) for x in m.paths_to_leaves()]
                    maxLengths = np.argwhere(lengths == np.amax(lengths)).flatten()
                    print("Number of computed paths : {}".format(len(lengths)))
                    print("Number of valid paths    : {}".format(len(maxLengths)))


    # evaluate(StartingBoard, printTree=True)
    # evaluate(PawnJumps, printTree=True)
    # evaluate(KingJumps)
    # evaluate(KingZigzag, printTree=False, printPaths=True)