from dama.game.gameboard import Gameboard
from dama.game.rules import Rules
from dama.game.constants import Color
import numpy as np
import unittest

class TestSlideMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.gameboard = Gameboard()

    def test_valid(self):
        self.assertEqual(Rules.is_valid_slide(self.gameboard, Color.WHITE, np.array([5, 0]), np.array([4, 0])), True)

    def test_nomove(self):
        self.assertEqual(Rules.is_valid_slide(self.gameboard, Color.WHITE, np.array([5, 0]), np.array([5, 0])), False)

    def test_diagonal(self):
        self.assertEqual(Rules.is_valid_slide(self.gameboard, Color.WHITE, np.array([5, 0]), np.array([4, 1])), False)

    def test_outofboard(self):
        self.assertEqual(Rules.is_valid_slide(self.gameboard, Color.WHITE, np.array([5, 0]), np.array([5, -1])), False)

    def test_occupied(self):
        self.assertEqual(Rules.is_valid_slide(self.gameboard, Color.WHITE, np.array([5, 0]), np.array([5, 1])), False)

if __name__ == '__main__':
    unittest.main()