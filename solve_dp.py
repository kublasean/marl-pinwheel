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

class Agent:
    def __init__(self, states, i):
        self.v = {}
        self.pi = {}
        self.id = i
        for k in states.keys():
            self.pi[k] = [1.0/4 for i in range(4)]
            self.v[k] = 0.0

def actionValue(state, agent_action, agents, agent_id, g, gamma):
    val = 0.0
    for action in g.actions:
        pa = 1.0
        if action[agent_id] != agent_action:
            continue
        for i in range(len(action)):
            if agent_id == i:
                continue
            pa *= agents[i].pi[state][action[i]]
        g.init_ep(g.states[state])
        sn, r = g.move1(action)
        val += pa * (r + gamma * agents[agent_id].v[sn])
    return val

def calculateV(agents, g, gamma):
    delta = 1
    thresh = 0.001
    while(delta > thresh):
        delta = 0
        for i, agent in enumerate(agents):
            for s in g.states.keys():
                val = 0
                for a, pa in enumerate(agent.pi[s]):
                    val += pa * actionValue(s,a,agents,i,g,gamma)
                if delta < abs(val - agent.v[s]):
                    delta = abs(val - agent.v[s])
                agent.v[s] = val

def calculatePi(agents, agent_id, g, gamma):
    samepi = True
    agent = agents[agent_id]
    for s, agent_pos in g.states.items():
        g.init_ep(agent_pos)
        if g.isTerminal():
            continue
        rs = []
        for a in range(4):
            rs.append(actionValue(s,a,agents,agent_id,g,gamma))
        best = max(rs)
        num_best = 0
        new_pi = [1.0 for i in range(4)]
        for i, q in enumerate(rs):
            if q != best:
                new_pi[i] = 0.0
            else:
                num_best += 1
        for i in range(len(rs)):
            new_pi[i] /= num_best
            if agent.pi[s][i] != new_pi[i]:
                samepi = False
            agent.pi[s][i] = new_pi[i]
    return samepi


def multi_value_iteration(agents, g, gamma):
    delta = 1
    thresh = 0.001
    while(delta > thresh):
        delta = 0
        for i, agent in enumerate(agents):
            for s in g.states.keys():
                val = 0
                rs = []
                for a in range(4):
                    rs.append(actionValue(s,a,agents,i,g,gamma))
                val = max(rs)
                if delta < abs(val - agent.v[s]):
                    delta = abs(val - agent.v[s])
                agent.v[s] = val

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
            g.init_ep(agent_pos)
            if g.isTerminal():
                continue
            rs = []
            for a in actions:
                sn, r = g.move1(a)
                rs.append(r + gamma*v[sn])
                g.init_ep(agent_pos)
            newV = max(rs)
            if delta < abs(newV - v[s]):
                delta = abs(newV - v[s])
            v[s] = newV
    
    #derive policy
    for s, agent_pos in g.states.items():
        g.init_ep(agent_pos)
        if g.isTerminal():
            continue
        rs = []
        sns = []
        for a in actions:
            sn, r = g.move1(a)
            ret = r + gamma*v[sn]
            rs.append(ret)
            sns.append(sn)
            g.init_ep(agent_pos)
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
    usage = "./solve-dp game-file.p out-file"
    if len(args) != 3:
        print(usage)
        return -1

    config = pickle.load( open(args[1], "rb") )
    g = pinwheel(config)

    v, pi = value_iteration(g, config['v'], 0.9)
    
    pickle.dump(v, open("dp/"+args[2]+".v", "wb"))
    pickle.dump(pi, open("dp/"+args[2]+".pi", "wb"))

if __name__ == "__main__":
	main(sys.argv)