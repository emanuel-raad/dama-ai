from dama.game import dama
from dama.agents.placeholder import Placeholder 
from dama.tests.test_jumps_normal import rules
from dama.game.constants import Color

import numpy as np
import pickle
import os
import json
import time
import pprint

class base_model():
    def __init__(self, player, board):
        self.player = player
        self.board = board
        self.damagame = dama.DamaGame(board=board)

    def calc(self, position):
        self.tree = self.damagame.get_piece_legal_move(self.player, position)
        self.set = dama.setFromTree(self.tree)['move']

def test(j, compare=True):

    for rule in j:
        p = rule['player']

        test = base_model(p, rule['board'])

        for pos in rule['position']:
            start_time = time.time()
            test.calc(pos)
            end_time = time.time()
            runtime = end_time - start_time

            if p.color == Color.WHITE:
                color_str = 'white'
            else:
                color_str = 'black'

            filename = '{}_{}_{}x{}.pkl'.format(color_str, rule['label'], pos[0], pos[1])
            filename = os.path.join('dama', 'tests', 'test_jumps_normal', filename)

            if not compare:
                print(rule['label'])
                pprint.pprint(test.set)
                print()
                with open(filename, 'wb') as handle:
                    pickle.dump(test.set, handle)
            elif compare:
                with open(filename, 'rb') as handle:
                    actual = pickle.load(handle)
                    
                    # yield check_set_equality, actual, test.set
                    eq = check_set_equality(actual, test.set)
                    print("[{:4.0f}ms] {}: {}".format(runtime * 1000, eq, filename))

                    if not eq:
                        print("Actual: {}".format(actual))
                        print("Test: {}".format(test.set))
                        print()

def check_set_equality(set1, set2):
    return set1.difference(set2) == set()

if __name__ == '__main__':
    test(rules.rules, compare=True)