# sean whalen
# reads in a pickled blob (a dictionary of game config info)
# creates a class representing the game
# applies dp to it

import sys
import numpy as np
import copy
import pickle
import random
import operator
import itertools as it
from state_gen import print_board, getkey

def sample(probs):
    s = random.random()
    prev=0
    a = 0
    for p in probs:
        if s > prev and s < p+prev:
            return a
        prev += p
        a += 1
    print("error: sample")
    return None

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
        this.actions = [list(i) for i in it.product(range(4),repeat=this.nagents)]

    def init_ep(this):
        this.pos = copy.copy(this.starts)
        this.setpos()
    def isTerminal(this):
        for pos, goal in zip(this.pos, this.goals):
            if pos[0] != goal[0] or pos[1] != goal[1]:
                return False
        return True
    def setpos(this): 
        for i, (r, c) in enumerate(this.pos):
                this.board[r][c] = repr(i)
    def move(this, agent_actions, reset):
        new_pos = []
        taken = {}
        #set current positions
        for i, (r, c) in enumerate(this.pos):
            this.board[r][c] = repr(i)
    
        #find new positions
        for i, (pos, a) in enumerate(zip(this.pos, agent_actions)):
            row = pos[0]
            col = pos[1]
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
                row = pos[0]
                col = pos[1]
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
                    row = this.pos[i][0]
                    col = this.pos[i][1]
                    new_pos[i] = [row, col]
        
        #clear old positions
        for r, c in this.pos:
            this.board[r][c] = ' '
        
        #update agent positions
        for i, (r,c) in enumerate(new_pos):
            this.board[r][c] = repr(i)
        nextstate = getkey(this.board)

        this.pos = copy.copy(new_pos)
        if reset:
            for r,c in this.pos:
                this.board[r][c] = ' '
        
        #reward for finishing game
        if this.isTerminal():
            return nextstate, 0
        return nextstate, -1

    #doesn't reset anything
    def move1(this, agent_actions):
        new_pos = []
        taken = {}
        #find new positions
        for i, (pos, a) in enumerate(zip(this.pos, agent_actions)):
            row = pos[0]
            col = pos[1]
            if a == 0:
                row -= 1
            elif a == 1:
                col += 1
            elif a == 2:
                row += 1
            else:
                col -= 1
            #can only move onto space
            if this.board[row][col] != ' ':
                row = pos[0]
                col = pos[1]
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
                    row = this.pos[i][0]
                    col = this.pos[i][1]
                    new_pos[i] = [row, col]
        #clear old positions
        for r, c in this.pos:
            this.board[r][c] = ' '
        #update agent positions
        for i, (r,c) in enumerate(new_pos):
            this.board[r][c] = repr(i)
        nextstate = getkey(this.board)
        this.pos = new_pos
        #reward for finishing game
        if this.isTerminal():
            return nextstate, 0
        return nextstate, -1

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

    def test_game(this, pi):
        this.init_ep()
        while True:
            print_board(this.board)
            if this.isTerminal():
                break
            i = sample( pi[getkey(this.board)])
            action = this.actions[i]
            sn, r = this.move1(action)
            input()

def main(args):
    usage = "python pinwheel game-file.p policy-file.pi"
    if len(args) != 3:
        print(usage)
        return -1
    
    config = pickle.load( open(args[1], "rb") )
    pi = pickle.load( open(args[2], "rb"))
    g = pinwheel(config)
    g.test_game(pi)

if __name__ == "__main__":
	main(sys.argv)