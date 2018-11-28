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
from pinwheel import pinwheel

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
        for i, q in enumerate(rs):
            if q != best:
                pi[s][i] = 0.0
            else:
                num_best += 1
        for i in range(len(rs)):
            pi[s][i] /= num_best
    
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
    
    pickle.dump(v, open("dp/"+args[1]+".v", "wb"))
    pickle.dump(pi, open("dp/"+args[1]+".pi", "wb"))

if __name__ == "__main__":
	main(sys.argv)