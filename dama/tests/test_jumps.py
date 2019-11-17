from dama.game import dama
from dama.agents import player
from dama.game.constants import Color
from dama.tests import gameboards
import numpy as np
import pprint

class base_model():
    def __init__(self, player, board):
        self.player = player
        self.board = board
        self.damagame = dama.DamaGame()
        self.damagame.gameboard = board
    def calc(self, position):
        self.res = self.damagame.get_piece_legal_move(self.player, position)
        # self.res['tree'].show(data_property='position')
    def __eq__(self, other):
        return self.res['tree'].show(data_property='position') == other.res['tree'].show(data_property='position')

if __name__ == '__main__':
    
    print("Testing jumps...!")

    white = player.Player(Color.WHITE)
    black = player.Player(Color.BLACK)

    test1 = base_model(white, gameboards.branching_white)
    test1.calc(np.array([3, 3]))
    print(test1.res['tree'].paths_to_leaves())
    # test1.res['tree'].save2file('filename.txt', data_property='position')

    test2 = base_model(black, gameboards.branching_black)
    test2.calc(np.array([4, 3]))
    # print(test2.res['tree'].paths_to_leaves())

    tag_paths = []

    for i in test2.res['tree'].paths_to_leaves():
        path = []
        for j in i:
            path.append(test2.res['tree'].get_node(j).data.tag)
            # print("{} ".format(test2.res['tree'].get_node(j).data.tag)),
        tag_paths.append(path)
        # print()
    
    for i in tag_paths:
        print(i)

    s = set(map(tuple, tag_paths))
    s2 = set(map(tuple, tag_paths))