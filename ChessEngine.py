import sys
import PieceMovement as pm
from PieceMovement import *
from functools import partial
import cProfile
import time
import numpy as np
import random

################
#Engines
################

ENGINE="sf"
if ENGINE=="sf":
    hist = []#qs/ks==unsure
    import engines.sunfish.sunfish as sf
    from engines.sunfish.sunfish import Position as pos
    import engines.sunfish.tools.uci
#if ENGINE=="my-sf":
#    MOVETIME=2
#    hist = []#qs/ks==unsure
#    import engines.mySunfish.sunfish as sf
#    from engines.mySunfish.sunfish import Position as pos
#    import engines.mySunfish.tools.uci

#######################################
#TOOLS
#######################################
def fileAndRank(sqr:int)->tuple:
    return sqr%8, 7 - sqr//8

def getFen(colour:str)->str:
    piece_arr=np.array(["OO"]*64,dtype="<U2")
    
    for piece in allpieces:
        for f in piece.piecelist:
            piece_arr[f]=str(piece)
    fen=""
    for rank in piece_arr.reshape((8,8)):
        empty=0
        for file in rank:
            if file == "OO":
                empty+=1
            else:
                if file[0]=="w":
                    file=file[1].upper()
                else:
                    file=file[1].lower()
                if empty==0:
                    fen+=file
                else:
                    fen+=str(empty)
                    fen+=file
                    empty=0
        fen+=str(empty) if empty!=0 else ""
        fen+="/"
    fen=fen[0:-2]
    fen=fen[::-1]
    fen+=(" "+colour)
    cs=updateCastlingRights()
    fen+=" "
    fen+="K"if cs[0][0] else ""
    fen+="Q"if cs[0][1] else ""
    fen+="k"if cs[1][0] else ""
    fen+="q"if cs[1][0] else ""
    fen+= " -"
    return fen

def boardhash()->str:
    fen=""
    for piece in allpieces:
        fen+=str(piece.piecelist)+str(piece)
    return fen

def getSfI(colour:str)->str:
    ind=0
    out=[]
    piece_arr=np.array(["OO"]*64,dtype="<U2")
    
    for piece in allpieces:
        for f in piece.piecelist:
            piece_arr[f]=str(piece)
    out.insert(ind,"         \n")
    out.insert(ind,"         \n")

    for rank in piece_arr.reshape((8,8)):
        r=" "
        
        for file in rank:
            if file == "OO":
                r+="."
            else:
                if file[0]=="w":
                    file=file[1].upper()
                else:
                    file=file[1].lower()
                r+=file
        r+="\n"
        out.insert(ind,r)
    out.insert(ind,"         \n")
    out.insert(ind,"         \n")
    n=""
    for l in out: n+=l
    if colour==BLACK:
        n=n[::-1].swapcase()
    return n

def toCoords(start:int,end:int,name=None,capture=None)->str:
    if not(name): name = pieceatsqr(start).name
    if not(capture): capture = pieceatsqr(end)
    if name == 'K':
        if abs(start-end) == 2: return 'O-O'
    elif abs(start-end) == 3: return 'O-O-O'
    pre = ('' if name == 'p' else name)
    if capture and name == 'p': pre += numtocoord(start)[0]
    if capture: pre += 'x'
    return pre + numtocoord(end)

def fromcoords(mv:str)->tuple:
    cF={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}

    return (cF[mv[0]]+(int(mv[1])-1)*8,cF[mv[2]]+(int(mv[3])-1)*8)

class Position:
    evaluation = 0
    movestart = 0
    moveend = 0
    mateIn = 0
    #plies = 0
    coords = ''
    def __str__(self)->str:
        return f"{self.movestart}, {self.moveend}"

move_num = 0
# Returns the "best" move for colour
def FindBest(colour:str)->Position:
    print(getFen(colour))
    if ENGINE=="sf":
        cs=updateCastlingRights()
        hist.append(pos(getSfI(colour), 0, cs[0], cs[1], numtocoord(curState.enPassant), 0))
        b=engines.sunfish.tools.uci.bestMove(sf,hist)
        best=fromcoords(b)
        p= Position()
        p.evaluation=0
        p.movestart=best[0]
        p.moveend=best[1]
        p.mateIn=0
        p.coords=toCoords(best[0],best[1],str(pieceatsqr(best[0])),bool(pieceatsqr(best[1]))) 
        print(p)
        print(b)
        print(best)
        MovePiece(best[0],best[1])
        cs=updateCastlingRights()
        hist.append(pos(getSfI(colour), 0, cs[0], cs[1], numtocoord(curState.enPassant), 0))
        UndoMove()
        return p
        
    #if ENGINE=="my-sf":
    #    cs=updateCastlingRights()
    #    hist.append(pos(getSfI(colour), 0, cs[0], cs[1], numtocoord(curState.enPassant), 0))
    #    b=engines.mySunfish.tools.uci.bestMove(sf,hist,MOVETIME)
    #    best=fromcoords(b)
    #    p= Position()
    #    p.evaluation=0
    #    p.movestart=best[0]
    #    p.moveend=best[1]
    #    p.mateIn=0
    #    p.coords=toCoords(best[0],best[1],str(pieceatsqr(best[0])),bool(pieceatsqr(best[1]))) 
    #    print(p)
    #    print(b)
    #    print(best)
    #    MovePiece(best[0],best[1])
    #    cs=updateCastlingRights()
    #    hist.append(pos(getSfI(colour), 0, cs[0], cs[1], numtocoord(curState.enPassant), 0))    
    #    UndoMove()
    #    
    #    return p

if __name__ == '__main__':
    print(getSfI(WHITE))
    MovePiece(12, 28)
    print(getSfI(BLACK))
    MovePiece(52, 36)
    print(getSfI(WHITE))
    MovePiece(3, 12)
    print(getSfI(BLACK))
    cProfile.run('FindBest("b")')
    
    