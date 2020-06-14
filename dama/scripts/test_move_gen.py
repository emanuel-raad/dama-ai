import time

from treelib import Node, Tree

from dama.game.bitboard import Bitboard, initialize_board, single, print_bitboard
from dama.game.attack_routines import move_search, move_search_parallel, move_search_parallel2

if __name__ == '__main__':

    myPawn = initialize_board([1, 2])
    # myPawn = single(18)
    myKing = 0
    oppPawn = initialize_board([5, 6])
    # oppPawn = single(48)
    oppKing = 0
    board = Bitboard(myPawn, myKing, oppPawn, oppKing)

    time1 = time.time()
    tree = move_search_parallel2(board, 4)
    time2 = time.time()

    size = tree.size()
    totalTime = 1000*(time2 - time1)
    print("Generated {} states in : {:.4f}ms".format(size, totalTime))
    print("Tree depth             : {}".format(tree.depth()))
    print("Average time per move  : {:.4f}ms".format(totalTime/size))

    # regularTimes = []
    # parallelTimes = []
    # size = []

    # n = 6

    # for i in range(0, n):
    #     print('Running depth={}...'.format(i))
    #     time1 = time.time()
    #     tree = move_search(board, i)
    #     time2 = time.time()
    #     tree2 = move_search_parallel2(board, i)
    #     time3 = time.time()

    #     regularTimes.append(1000*(time2 - time1))
    #     parallelTimes.append(1000*(time3 - time2))

    #     assert tree.size() == tree2.size()
    #     size.append(tree.size())

    # for path1, path2 in zip(tree.paths_to_leaves(), tree2.paths_to_leaves()):
    #     for nodeID_1, nodeID_2 in zip(path1, path2):
    #         board1 = tree.get_node(nodeID_1).data.bitboards.board
    #         board2 = tree2.get_node(nodeID_2).data.bitboards.board
    #         assert board1 == board2

    # print("x  size      {:12}{:12}".format('regular', 'parallel'))
    # for i in range(0, n):
    #     print("{} {:5} {:10.1f}ms {:10.1f}ms".format(i, size[i], regularTimes[i], parallelTimes[i]))

    '''

    0 -> 9 states in 5 ms
    1 -> 73 states in 16 ms
    2 -> 781 states in 130 ms
    3 -> 8293 states in 1280 ms
    4 -> 91935 states in 14630 ms
    5 -> 994317 states in 158472 ms
    6 -> memory error lol

    Averages out to 0.160 ms per state

    '''