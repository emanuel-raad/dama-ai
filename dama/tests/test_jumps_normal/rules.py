import numpy as np

from dama.tests import gameboard_constants
from dama.agents.placeholder import Placeholder 
from dama.game.constants import Color

rules = [
    
    {
        "player":Placeholder(Color.WHITE),
        "board":gameboard_constants.simple,
        "label":"simple",
        "position": [
            np.array([4, 0]),
            np.array([4, 1])
        ]
    },

    {
        "player":Placeholder(Color.WHITE),
        "board":gameboard_constants.default,
        "label":"default",
        "position": [
            np.array([0, 0]),
            np.array([2, 1])
        ]
    },

    {
        "player":Placeholder(Color.BLACK),
        "board":gameboard_constants.jumpThenPromote,
        "label":"jumpThenPromote",
        "position": [
            np.array([4, 4]),
        ]
    },

    {
        "player":Placeholder(Color.BLACK),
        "board":gameboard_constants.zigzag,
        "label":"zigzag",
        "position": [
            np.array([7, 0]),
        ]
    },

]
