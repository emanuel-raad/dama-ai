import numpy as np
from dama.game.constants import Color

def get_last_direction(startPosition, endPosition):
    direction = startPosition - endPosition
    
    for i, element in enumerate(direction):
        if element > 0:
            direction[i] = 1
        elif element < 0:
            direction[i] = -1

    return direction

def get_valid_directions(startPosition, endPosition, color, promoted):
    valid_directions = np.array([[1, 0], [-1, 0], [0, -1], [0, 1]])

    if promoted:
        return valid_directions
    else:
        if startPosition is not None:
            last_direction = get_last_direction(startPosition, endPosition)            
            idx = np.where((valid_directions == last_direction).all(axis=1))
            valid_directions = np.delete(valid_directions, idx, axis=0)

        if color == Color.WHITE:
            backwards = np.array([1, 0])
        elif color == Color.BLACK:
            backwards = np.array([-1, 0])

        idx = np.where((valid_directions == backwards).all(axis=1))
        valid_directions = np.delete(valid_directions, idx, axis=0)
        
        return valid_directions

if __name__ == '__main__':
    startPosition = np.array([1, 2])
    endPosition = np.array([1, 4])

    print(get_valid_directions(None, endPosition, Color.BLACK, False))