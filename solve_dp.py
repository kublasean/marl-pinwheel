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
    def test_game(this, v, pi):
        this.pos = [[this.starts[i][0], this.starts[i][1]] for i in range(this.nagents)]
        this.setpos()
        while True:
            print_board(this.board)
            #print([(a, b) for a, b in zip(pi[getkey(this.board)], this.actions)])
            if this.isTerminal():
                break
            i = sample( pi[getkey(this.board)])
            #print((i,pi[getkey(this.board)][i]))
            action = this.actions[i]
            #print(action)
            sn, r = this.move(action, False)
            print(v[sn])
            input()

def value_iteration(g, v, gamma):
    pi = {}
    thresh = 0.0001
    delta = 1
    actions = g.actions
    for k in v.keys():
        pi[k] = [1.0 for i in range(len(actions))]
    
    #converge on value function
    while delta > thresh:
        delta = 0
        for s, agent_pos in g.states.items():
            g.pos = copy.copy(agent_pos)
            if g.isTerminal():
                continue
            rs = []
            for a in actions:
                g.pos = copy.copy(agent_pos)
                sn, r = g.move(a, True)
                rs.append(r + gamma*v[sn])
            newV = max(rs)
            if delta < abs(newV - v[s]):
                delta = abs(newV - v[s])
            v[s] = newV
    
    #derive policy
    for s, agent_pos in g.states.items():
        g.pos = copy.copy(agent_pos)
        #print("--state--")
        #print(s)
        if g.isTerminal():
            continue
        rs = []
        sns = []
        for a in actions:
            g.pos = copy.copy(agent_pos)
            sn, r = g.move(a, True)
            ret = r + gamma*v[sn]
            rs.append(ret)
            sns.append(sn)
        best = max(rs)
        num_best = 0
        #print("--best next states--")
        for i, q in enumerate(rs):
            if q != best:
                pi[s][i] = 0.0
            else:
                num_best += 1
                #print(sns[i])
        for i in range(len(rs)):
            pi[s][i] /= num_best
        #input()
    
    #print policy
    '''for s,pa in pi.items():
        out = copy.deepcopy(g.board)
        for i in range(len(pa)):
            if pa[i] != 0.0:
                for j in range(g.nagents):
                    r,c = g.states[s][j]
                    a = actions[i][j]
                    if a == 0:
                        out[r][c] = '^'
                    elif a == 1:
                        out[r][c] = '>'
                    elif a == 2:
                        out[r][c] = 'v'
                    elif a == 3:
                        out[r][c] = '<'
                break
        print(getkey(out))'''              
    return v, pi

def main(args):
    usage = "./solve-dp game-file.p"
    if len(args) != 2:
        print(usage)
        return -1

    config = pickle.load( open(args[1], "rb") )
    g = pinwheel(config)
    v, pi = value_iteration(g, config['v'], 1.0)
    #sort_v = sorted(v.items(), key=operator.itemgetter(1))
    g.test_game(v, pi)
    #for a, b in sort_v:
    #    print(a)
    #    print(b)

if __name__ == "__main__":
	main(sys.argv)