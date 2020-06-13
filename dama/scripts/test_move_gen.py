import time

from treelib import Node, Tree

from dama.game.bitboard import Bitboard, initialize_board
from dama.game.attack_routines import move_search

if __name__ == '__main__':

    # print(get_active_indices(9223372036854775808))

    myPawn = initialize_board([1, 2])
    # myPawn = single(40)
    myKing = 0
    oppPawn = initialize_board([5, 6])
    # oppPawn = single(48)
    oppKing = 0
    board = Bitboard(myPawn, myKing, oppPawn, oppKing)

    time1 = time.time()
    tree = move_search(board, 4)

    time2 = time.time()

    size = tree.size()
    totalTime = 1000*(time2 - time1)
    print("Generated {} states in : {:.4f}ms".format(size, totalTime))
    print("Tree depth             : {}".format(tree.depth()))
    print("Average time per move  : {:.4f}ms".format(totalTime/size))

    '''

    0 -> 9 states in 5 ms
    1 -> 73 states in 16 ms
    2 -> 781 states in 130 ms
    3 -> 8293 states in 1280 ms
    4 -> 91935 states in 14630 ms
    5 -> 992873 states in 158472 ms

    Averages out to 0.160 ms per state

    '''