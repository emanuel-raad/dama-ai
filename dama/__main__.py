from dama.game import dama
from dama.agents.placeholder import Placeholder
from dama.game.constants import Color
from dama.tests.gameboards_constants import tripleJumpPromotedMiddle
from dama.tests.gameboards_constants import simple
from dama.tests.gameboards_constants import default
import numpy as np
import pprint

if __name__ == '__main__':

    print("Hello World!")

    damagame = dama.DamaGame(board=tripleJumpPromotedMiddle)

    # white = player.Player(Color.WHITE)
    # black = player.Player(Color.BLACK)

    white = Placeholder(Color.WHITE)
    black = Placeholder(Color.BLACK)

    print("STARTING BOARD")
    print(damagame.gameboard.gameboard)
    print()

    tests = [
        [white, np.array([[1, 0]])],
        # [black, np.array([[1, 0]])],
    ]

    for i in tests:
        player = i[0]

        res = damagame.get_all_legal_moves(player=player)
        pprint.pprint(res['move'])

        print(damagame.getMetricsAfterMove(player, res['move'][0], res['remove'][0]))

        # for position in i[1]:
        #     tree = damagame.get_piece_legal_move(player, position)
        #     tree.show(data_property='position')
            
        #     b =  dama.listFromTree(tree)
            
        #     move_list = b['move']
        #     remove_list = b['remove']
        #     count_list = b['count']

        #     for move, remove, count in zip(move_list, remove_list, count_list):
        #         print("{:<10}: {}".format('move', move))
        #         print("{:<10}: {}".format('remove', remove))
        #         print("{:<10}: {}".format('count', count))
        #         print()


        # for position in i[1]:
        #     tree = damagame.get_piece_legal_move(player, position)
        #     # print("Piece: {} Moves: {}".format(position, res['legal_moves']))
        #     tree.show(data_property='position')
            
        #     b =  dama.listFromTree(tree)
        #     move_list = b['move']
        #     remove_list = b['remove']
        #     count_list = b['count']

        #     max_indices = np.argwhere(count_list == np.amax(count_list)).flatten().tolist()
        #     print(max_indices)
    
        #     for move, remove, count in zip(move_list, remove_list, count_list):
        #         print("{:<10}: {}".format('move', move))
        #         print("{:<10}: {}".format('remove', remove))
        #         print("{:<10}: {}".format('count', count))
        #         print()

        #     damagame.gameboard = tripleJumpPromotedMiddle

        # print()