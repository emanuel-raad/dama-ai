from dama.game import dama
from dama.agents import player
from dama.game.constants import Color
from dama.tests.test_jumps_normal import rules
import numpy as np
import pickle
import os
import json

class base_model():
    def __init__(self, player, board):
        self.player = player
        self.board = board
        self.damagame = dama.DamaGame()
        self.damagame.gameboard = board
    def calc(self, position):
        self.res = self.damagame.get_piece_legal_move(self.player, position)
        self.tree2set()
    def tree2set(self):
        tag_paths = []

        for i in self.res['tree'].paths_to_leaves():
            path = []
            for j in i:
                path.append(self.res['tree'].get_node(j).data.tag)
            tag_paths.append(path)
        
        self.set = set(map(tuple, tag_paths))

def test(j, compare=True):

    for json in j:
        if json['player'] == 'white':
            p = player.Player(Color.WHITE)
        elif json['player'] == 'black':
            p = player.Player(Color.BLACK)

        for rule in json['tests']:

            test = base_model(p, rule['board'])

            for s in rule['start']:
                test.calc(s)
                filename = '{}_{}_{}x{}.pkl'.format(json['player'], rule['label'], s[0], s[1])
                filename = os.path.join('dama', 'tests', 'test_jumps_normal', filename)

                if not compare:
                    with open(filename, 'wb') as handle:
                        pickle.dump(test.set, handle)
                elif compare:
                    with open(filename, 'rb') as handle:
                        actual = pickle.load(handle)
                        
                        # yield check_set_equality, actual, test.set
                        print("{}: {}".format(check_set_equality(actual, test.set), filename))

# def check_set_equality(set1, set2):
#     assert set1.difference(set2) == set()

def check_set_equality(set1, set2):
    return set1.difference(set2) == set()

if __name__ == '__main__':
    test(rules.rules, compare=True)