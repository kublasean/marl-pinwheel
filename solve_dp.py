# sean whalen
# reads in a pickled blob (a dictionary of game config info)
# creates a class representing the game
# applies dp to it

import sys
import numpy as np
import copy
import pickle
import itertools as it
from state_gen import print_board, getkey

class pinwheel:
    def __init__(this, config):
        this.board = config['board']
        this.nrows = config['nrows']
        this.ncols = config['ncols']
        this.nagents = config['nagents']
        this.starts = config['starts']
        this.states = config['states']
        this.goals = config['goals']
        this.pos = [[this.starts[i][0], this.starts[i][1]] for i in range(this.nagents)] 
    def isTerminal(this):
        for pos, goal in zip(this.pos, this.goals):
            if pos[0] != goal[0] or pos[1] != goal[1]:
                return False
        return True
    def move(this, agent_actions, reset):
        new_pos = []
        taken = {}

        #set current positions
            for i, (r, c) in enumerate(this.pos):
                this.board[r][c] = repr(i)
        
        #find new positions
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
            #can only move onto space
            if this.board[row][col] != ' ':
                row, col = pos
            key = repr(row)+repr(col)
            if key in taken:
                taken[key].append(i)
            else:
                taken[key] = [i]
            new_pos.append([row,col])

        #agent collisions
        if len(taken) != this.nagents:
            for k,v in taken.items():
                if len(v) == 1:
                    continue
                for i in v:
                    row, col = this.pos[i]
                    new_pos[i] = [row, col]
        
        #clear old positions
        for r, c in this.pos:
            this.board[r][c] = ' '
        
        #update agent positions
        this.pos = new_pos
        for i, (r,c) in enumerate(this.pos):
            this.board[r][c] = repr(i)
        nextstate = getkey(this.board)

        if reset:
            for r,c in this.pos:
                this.board[r][c] = ' ' 
        
        #reward for finishing game
        if this.isTerminal():
            return nextstate, 1
        return nextstate, 0

    def play_game(this):
        while True:
            #set current positions
            for i, (r, c) in enumerate(this.pos):
                this.board[r][c] = repr(i)
            print_board(this.board)
            line = input()
            actions = line.strip().split()
            if len(actions) != this.nagents:
                break
            agent_actions = []
            for a in actions:
                if a == 'w':
                    agent_actions.append(0)
                elif a == 'd':
                    agent_actions.append(1)
                elif a == 's':
                    agent_actions.append(2)
                elif a == 'a':
                    agent_actions.append(3)
                else:
                    break
            if this.move(agent_actions, False):
                break
    
def value_iteration(g, v, gamma):
    pi = {}
    
    thresh = 0.0001
    delta = 1
    actions = [i for i in it.product(range(4),repeat=this.nagents)]
    for k in v.keys():
        pi[k] = np.ones((nagents,4))
    
    #converge on value function
    while delta > thresh:
        delta = 0
        for s, agent_pos in g.states.items():
            g.pos = agent_pos
            if game.isTerminal():
                continue
            rs = []
            for a in actions:
                sn, r = game.move(a)
                rs.append(r + gamma*v[sn])
            newV = max(rs)
            if delta < abs(newV - v[s]):
                delta = abs(newV - v[s])
            v[s] = newV
    
    #derive policy
    for s, agent_pos in g.states.items():
        g.pos = agent_pos
        if game.isTerminal():
            continue
        rs = []
        for a in actions:
            sn, r = game.move(a)
            rs.append(r + gamma*v[sn])
        best = max(rs)
        num_best = 0
        for i, q in enumerate(rs):
            if q != best:
                pi[s] 

    return v, pi

def main(args):
    usage = "./solve-dp game-file.p"
    if len(args) != 2:
        print(usage)
        return -1

    config = pickle.load( open(args[1], "rb") )
    g = pinwheel(config)
    g.play_game()
    

if __name__ == "__main__":
	main(sys.argv)