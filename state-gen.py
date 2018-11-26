# sean whalen
# reads in a game file
# outputs a list of valid states
# TODO just blob the s dictionary with pickle?

import sys
import numpy as np
import copy

def print_board(board):
    for line in board:
        out = ""
        for cell in line:
            out += cell
        print(out)
    print()
        
def getkey(board):
    key = ""
    for row in board:
        key += ''.join(row) + '\n'
    return key
        
def main(args):
    usage = "./state-gen.py game-file"
    
    if len(args) != 2:
        print(usage)
        return -1
    
    nrows = None
    ncols = None
    nagent = None
    board = []
    space = []
    starts = []
    s = {}
    
    with open(args[1], "r") as f:
        fields = f.readline().split(" ")
        nrows = int(fields[0])
        ncols = int(fields[1])
        nagent = int(f.readline())
        for line in f:
            board.append(list(line.strip()))
        #print_board(board)

    for i in range(nrows):
        for j in range(ncols):
            if board[i][j] == '.':
                starts.append((i,j))
            if board[i][j] == '.' or board[i][j] == ' ':
                space.append((i,j))
    
    out = copy.deepcopy(board)
    for i,j in space:
        out[i][j] = ' '
    
    #TODO turn this into one recursive function instead of this mess
    if nagent == 1:
        for i,j in space:
            out[i][j] = '0'
            s[getkey(out)] = 0.0
            out[i][j] = ' '
    elif nagent == 2:
        for i,j in space:
            out[i][j] = '0'
            for ii, jj in space:
                if out[ii][jj] != ' ':
                    continue
                out[ii][jj] = '1'
                s[getkey(out)] = 0.0
                out[ii][jj] = ' '
            out[i][j] = ' '
    elif nagent == 3:
        for i,j in space:
            out[i][j] = '0'
            for ii, jj in space:
                if out[ii][jj] != ' ':
                    continue
                out[ii][jj] = '1'
                for iii, jjj in space:
                    if out[iii][jjj] != ' ':
                        continue
                    out[iii][jjj] = '2'
                    s[getkey(out)] = 0.0
                    out[iii][jjj] = ' '
                out[ii][jj] = ' '
            out[i][j] = ' '
    elif nagent == 4:
        for i,j in space:
            out[i][j] = '0'
            for ii, jj in space:
                if out[ii][jj] != ' ':
                    continue
                out[ii][jj] = '1'
                for iii, jjj in space:
                    if out[iii][jjj] != ' ':
                        continue
                    out[iii][jjj] = '2'
                    for iiii, jjjj in space:
                        if out[iiii][jjjj] != ' ':
                            continue
                        out[iiii][jjjj] = '3'
                        s[getkey(out)] = 0.0
                        out[iiii][jjjj] = ' '
                    out[iii][jjj] = ' '
                out[ii][jj] = ' '
            out[i][j] = ' '
    
    print(len(s))  
    for skey in s.keys():
        print(skey)
    return 0

if __name__ == "__main__":
	main(sys.argv)
