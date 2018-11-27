# sean whalen
# reads in a pickled blob (a dictionary of game config info)
# creates a class representing the game
# applies dp to it

import sys
import numpy as np
import copy
import pickle
from state_gen import print_board, getkey

class pinwheel:
    def __init__(this, config):
        this.board = config['board']
        this.nrows = config['nrows']
        this.ncols = config['ncols']
        this.nagents = config['nagents']
        this.starts = config['starts']
        this.copy_v = config['v']
        this.goals = [this.starts[(i+1) % this.nagents] for i in range(this.nagents)]
        this.pos = [[this.starts[i][0], this.starts[i][1]] for i in range(this.nagents)] 
    def isTerminal(this):
        for pos, goal in zip(this.pos, this.goals):
            if pos[0] != goal[0] or pos[1] != goal[1]:
                return False
        return True
    def move(this, agent_actions, reset):
        new_pos = []
        #pos: position of agent, a: agent action
        for i, (pos, a) in enumerate(zip(this.pos, agent_actions)):
            row, col = pos
            #N
            if a == 0:
                row -= 1
            #E
            elif a == 1:
                col += 1
            #S
            elif a == 2:
                row += 1
            #W
            else:
                col -= 1
            key = repr(row)+repr(col)

            #going out of bounds
            if this.board[row][col] == 'x':
                row, col = pos
            #another agent occupies
            elif this.board[row][col] != ' ':
                row, col = pos
                other_id = int(this.board[row][col])
                new_pos[other_id][0] = this.pos[other_id][0]
                new_pos[other_id][1] = this.pos[other_id][1]
            new_pos.append([row, col])
            board[row][col] = repr(i)
            
            return sn, 0

    
def value_iteration(game, gamma):
    v = np.zeros((game.dim, game.dim))
    pi = np.ones((game.dim, game.dim, game.actions))
    thresh = 0.0001
    delta = 1
    #converge on value function
    while delta > thresh:
        delta = 0
        for i in range(game.dim):
            for j in range(game.dim):
                s = state(i,j)
                if game.isTerminal(s):
                    continue
                rs = np.zeros(game.actions)
                for a in range(game.actions):
                    sn, r = game.getNextSR(s,a)
                    rs[a] = r + gamma*v[sn.row,sn.col]
                newV = np.amax(rs)
                if delta < abs(newV - v[i,j]):
                    delta = abs(newV - v[i,j])
                v[i,j] = newV
    #derive policy
    for i in range(game.dim):
        for j in range(game.dim):
            s = state(i,j)
            rs = np.zeros(game.actions)
            for a in range(game.actions):
                    sn, r = game.getNextSR(s,a)
                    rs[a] = r + gamma*v[sn.row,sn.col]
            bestMoves = rs == np.amax(rs)
            numOfMoves = np.sum(bestMoves)
            for a in range(game.actions):
                if bestMoves[a]:
                    pi[i,j,a] = 1.0/numOfMoves
                else:
                    pi[i,j,a] = 0.0
    return v, pi

def main(args):
    usage = "./solve-dp game-file.p"
    if len(args) != 2:
        print(usage)
        return -1

    config = pickle.load( open(args[1], "rb") )
    g = pinwheel(config)

    print(getkey(g.board))
    print(g.starts)
    print(g.goals)

    print(g.pos)

if __name__ == "__main__":
	main(sys.argv)