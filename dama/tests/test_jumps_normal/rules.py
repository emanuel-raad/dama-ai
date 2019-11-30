from dama.tests import gameboards
import numpy as np

rules = [
    {
        "player":"white",
        "tests": [
            {
                "board":gameboards.simple,
                "label":"simple",
                "start": [
                    np.array([4, 0]),
                    np.array([4, 1])
                ]
            },
            {
                "board":gameboards.default,
                "label":"default",
                "start": [
                    np.array([0, 0]),
                    np.array([2, 1])
                ]
            },
        ]
    },
    {
        "player":"black",
        "tests": [
            {
                "board":gameboards.branching_black,
                "label":"branching_black",
                "start": [
                    np.array([4, 3]),
                ]
            },
        ]
    }
]
