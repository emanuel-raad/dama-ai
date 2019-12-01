from dama.agents.player import Player
import numpy as np

class Human(Player):
    def request_move(self, moveList, removeList):
        maxChoice = len(moveList) - 1
        
        for i, move in enumerate(moveList):
            readable = []
            for j in range(len(move)):
                readable.append(np.array2string(move[j]))
            print("{}: {}".format(i, readable))


        choice = -1
        while choice < 0 or choice > maxChoice:
            try:
                choice = int(input("Enter a move: "))
            except ValueError:
                print("Not a valid move")
        
        return choice