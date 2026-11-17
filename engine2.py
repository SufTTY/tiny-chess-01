import json,os,sys,urllib.request,urllib.error
U=os.environ.get("MAKEFUN_ENV_URL")
def post(p,b):
    r=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
    try:
        with urllib.request.urlopen(r,timeout=30) as x:return json.load(x)
    except urllib.error.HTTPError as e:sys.exit("env %s %s"%(e.code,e.read()[:200]))

# ---------- board: 10x12 mailbox, 0..119, off-board = None ----------
W=10
A=[r*W+c for r in range(2,10) for c in range(1,9)]   # 0..63 -> square, a8 first
SQI={s:i for i,s in enumerate(A)}                    # square -> 0..63 (a8=0,h1=63)
OFF={'N':(-21,-19,-12,-8,8,12,19,21),'B':(-11,-9,9,11),'R':(-10,-1,1,10)}
OFF['Q']=OFF['B']+OFF['R'];OFF['K']=OFF['Q']
VAL={'P':100,'N':325,'B':335,'R':500,'Q':1000,'K':0}
PST={
'P':(0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0),
'N':(-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50),
'B':(-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20),
'R':(0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0),
'Q':(-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20),
'K':(20,30,10,0,0,10,30,20,20,20,0,0,0,0,20,20,-10,-20,-20,-20,-20,-20,-20,-10,-20,-30,-30,-40,-40,-30,-30,-20,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30)}
PSTB={}
for _pc in PST:
    _t=[0]*120
    for _i,_s in enumerate(A):
        _t[_s]=PST[_pc][_i]
    PSTB[_pc]=_t
PSTW={}
for _pc in PST:
    _t=[0]*120
    for _i,_s in enumerate(A):
        _t[_s]=PST[_pc][63-_i]
    PSTW[_pc]=_t
def pstv(p,s):
    if p.isupper():
        return PSTW[p][s]
    return PSTB[p.upper()][s]

class Pos:
    __slots__=('b','stm','cr','ep','score','wk','bk','nm')
    def __init__(P,**k):
        for a in Pos.__slots__:setattr(P,a,k[a])
def parse(fen):
    b=[None]*120
    for s in A:b[s]='.'
    parts=fen.split()
    r=2;c=1
    for ch in parts[0]:
        if ch=='/':r+=1;c=1
        elif ch.isdigit():c+=int(ch)
        else:b[r*W+c]=ch;c+=1
    stm=1 if parts[1]=='w' else -1
    cr=0
    if 'K' in parts[2]:cr|=1
    if 'Q' in parts[2]:cr|=2
    if 'k' in parts[2]:cr|=4
    if 'q' in parts[2]:cr|=8
    ep=-1
    if len(parts)>3 and parts[3]!='-':
        ep=(9-int(parts[3][1]))*W+1+"abcdefgh".index(parts[3][0])
    sc=0;wk=bk=0;nm=0
    for s in A:
        p=b[s]
        if p=='.':continue
        v=VAL[p.upper()]
        if p.upper()!='P' and p.upper()!='K':nm+=v
        sc+=(VAL[p.upper()]+pstv(p,s))*(1 if p.isupper() else -1)
        if p=='K':wk=s
        elif p=='k':bk=s
    return Pos(b=b,stm=stm,cr=cr,ep=ep,score=sc,wk=wk,bk=bk,nm=nm)

def attacked(P,sq,bywhite):
    b=P.b
    if bywhite:
        # pawns attack square from below-left/right (white pawns move up)
        if b[sq+9]=='P' or b[sq+11]=='P':return True
        k='N'
        for o in OFF['N']:
            if b[sq+o]==k:return True
        for o in OFF['K']:
            if b[sq+o]=='K':return True
        for o in OFF['B']+OFF['R']:
            t=sq+o;dd=None
            while True:
                q=b[t]
                if q is None:break
                if q!='.':
                    if q.isupper():
                        if q=='Q' or (q=='B' and o in OFF['B']) or (q=='R' and o in OFF['R']):return True
                    break
                t+=o
    else:
        if b[sq-9]=='p' or b[sq-11]=='p':return True
        for o in OFF['N']:
            if b[sq+o]=='n':return True
        for o in OFF['K']:
            if b[sq+o]=='k':return True
        for o in OFF['B']+OFF['R']:
            t=sq+o
            while True:
                q=b[t]
                if q is None:break
                if q!='.':
                    if q.islower():
                        if q=='q' or (q=='b' and o in OFF['B']) or (q=='r' and o in OFF['R']):return True
                    break
                t+=o
    return False

def gen(P,out):
    b=P.b;w=P.stm>0;ep=P.ep
    for s in A:
        p=b[s]
        if p=='.':continue
        up=p.isupper()
        if up!=w:continue
        t=p.upper()
        if t=='P':
            one=s-10 if up else s+10
            if b[one]=='.':
                if (up and one<30) or (not up and one>89):
                    for i,pr in enumerate('NBRQ' if up else 'nbrq'):
                        out.append(s|one<<7|(i+1)<<14)
                else:
                    out.append(s|one<<7)
                    two=s-20 if up else s+20
                    if (up and s>80) or (not up and s<39):
                        if b[two]=='.':out.append(s|two<<7)
            for o in ((-11,-9) if up else (9,11)):
                t2=s+o;q=b[t2]
                if q is not None and q!='.' and q.isupper()!=up:
                    if (up and t2<30) or (not up and t2>89):
                        for i,pr in enumerate('NBRQ' if up else 'nbrq'):
                            out.append(s|t2<<7|(i+1)<<14)
                    else:out.append(s|t2<<7)
                elif t2==ep and ep>0:out.append(s|t2<<7|1<<20)
        else:
            for o in OFF[t]:
                t2=s+o
                while True:
                    q=b[t2]
                    if q is None:break
                    if q=='.':
                        out.append(s|t2<<7)
                        if t=='N' or t=='K':break
                        t2+=o
                    else:
                        if q.isupper()!=up:out.append(s|t2<<7)
                        break
    # castling
    if w:
        if P.cr&1 and b[95]=='K' and b[96]=='.' and b[97]=='.' and b[98]=='R' \
           and not attacked(P,95,0) and not attacked(P,96,0) and not attacked(P,97,0):
            out.append(95|97<<7)
        if P.cr&2 and b[95]=='K' and b[94]=='.' and b[93]=='.' and b[92]=='.' and b[91]=='R' \
           and not attacked(P,95,0) and not attacked(P,94,0) and not attacked(P,93,0):
            out.append(95|93<<7)
    else:
        if P.cr&4 and b[25]=='k' and b[26]=='.' and b[27]=='.' and b[28]=='r' \
           and not attacked(P,25,1) and not attacked(P,26,1) and not attacked(P,27,1):
            out.append(25|27<<7)
        if P.cr&8 and b[25]=='k' and b[24]=='.' and b[23]=='.' and b[22]=='.' and b[21]=='r' \
           and not attacked(P,25,1) and not attacked(P,24,1) and not attacked(P,23,1):
            out.append(25|23<<7)
    return out

def make(P,m):
    b=P.b
    f=m&127;t=(m>>7)&127;pr=(m>>14)&7;fl=(m>>20)&1
    p=b[f];w=p.isupper();d=1 if w else -1
    if fl:
        vsq=t+10 if w else t-10
        cap=b[vsq];eflag=1
    else:
        cap=b[t];eflag=0;vsq=0
    undo=(f,t,cap,eflag,vsq,P.cr,P.ep,P.score,P.wk,P.bk,p)
    if eflag:
        b[vsq]='.'
        P.score+=d*(VAL[cap.upper()]+pstv(cap,vsq))
    elif cap!='.':
        P.score+=d*(VAL[cap.upper()]+pstv(cap,t))
    b[t]=p;b[f]='.'
    P.score+=d*(pstv(p,t)-pstv(p,f))
    if pr:
        np_='NBRQ'[pr-1]
        np_=np_ if w else np_.lower()
        b[t]=np_
        P.score+=d*(VAL[np_.upper()]+pstv(np_,t)-VAL['P']-pstv(p,t))
    if p.upper()=='P' and abs(t-f)==20:
        P.ep=(f+t)//2
    else:P.ep=-1
    if p.upper()=='K':
        if w:P.wk=t;P.cr&=12
        else:P.bk=t;P.cr&=3
        if abs(t-f)==2:
            if t>f:
                b[f+1]=b[f+3];b[f+3]='.'
            else:
                b[f-1]=b[f-4];b[f-4]='.'
    if P.cr:
        c=P.cr
        if f==98 or t==98:c&=~1
        if f==91 or t==91:c&=~2
        if f==28 or t==28:c&=~4
        if f==21 or t==21:c&=~8
        P.cr=c
    P.stm=-P.stm
    return undo

def unmake(P,u):
    f,t,cap,eflag,vsq,cr,ep,sc,wk,bk,p=u
    b=P.b
    b[f]=p
    if eflag:
        b[t]='.'
        b[vsq]=cap
    else:
        b[t]=cap
    if p.upper()=='K' and abs(t-f)==2:
        if t>f:
            b[f+3]=b[f+1];b[f+1]='.'
        else:
            b[f-4]=b[f-1];b[f-1]='.'
    P.cr=cr;P.ep=ep;P.score=sc;P.wk=wk;P.bk=bk
    P.stm=-P.stm

def legal(P):
    ms=[];gen(P,ms);out=[]
    for m in ms:
        u=make(P,m)
        ks=P.wk if P.stm<0 else P.bk
        if not attacked(P,ks,P.stm>0):
            out.append(m)
        unmake(P,u)
    return out

def perft(P,d):
    if d==0:return 1
    n=0
    for m in legal(P):
        u=make(P,m)
        n+=perft(P,d-1)
        unmake(P,u)
    return n

def quies(P,a,b,depth):
    st=P.score if P.stm>0 else -P.score
    if st>=b:return st
    if st>a:a=st
    if depth<=0:return a
    ms=[];gen(P,ms)
    caps=[m for m in ms if (m>>20)&1 or P.b[(m>>7)&127]!='.' or (m>>14)&7]
    caps.sort(key=lambda m:-PSTV(P,m))
    for m in caps:
        u=make(P,m)
        # skip if own king hangs
        ks=P.wk if P.stm<0 else P.bk
        if attacked(P,ks,P.stm<0):
            unmake(P,u);continue
        sc=-quies(P,-b,-a,depth-1)
        unmake(P,u)
        if sc>=b:return sc
        if sc>a:a=sc
    return a

def PSTV(P,m):
    t=(m>>7)&127
    q=P.b[t]
    return 0 if q=='.' else (VAL[q.upper()]//10)

MATE=100000
TT={}
KILL=[None]*64
class Stop(Exception):pass
LIM=100000
NODES=0
def mvvlva(P,m):
    t=(m>>7)&127
    q=P.b[t]
    v=0 if q=='.' else VAL[q.upper()]
    if (m>>20)&1:v=1050
    pr=(m>>14)&7
    if pr:v+=8000+pr
    return v
def qsearch(P,a,b,d,ply):
    global NODES
    NODES+=1
    if NODES>LIM:raise Stop()
    ks=P.wk if P.stm>0 else P.bk
    ick=attacked(P,ks,P.stm<0)
    st=P.score if P.stm>0 else -P.score
    if not ick:
        if st>=b:return st
        if st>a:a=st
        if d<=0:return a
    ms=[];gen(P,ms)
    caps=[]
    for m in ms:
        if ick:caps.append(m)
        else:
            t=(m>>7)&127
            if P.b[t]!='.' or (m>>20)&1 or (m>>14)&7:caps.append(m)
    if not caps:
        return -MATE+ply if ick else 0
    caps.sort(key=lambda m:-mvvlva(P,m))
    for m in caps:
        u=make(P,m)
        ks=P.wk if P.stm<0 else P.bk
        if attacked(P,ks,P.stm>0):
            unmake(P,u);continue
        sc=-qsearch(P,-b,-a,d-1,ply+1)
        unmake(P,u)
        if sc>=b:return sc
        if sc>a:a=sc
    return a
def search(P,d,a,b,ply):
    global NODES
    NODES+=1
    if NODES>LIM:raise Stop()
    ks=P.wk if P.stm>0 else P.bk
    if ply<24 and attacked(P,ks,P.stm<0):d+=1
    if d<=0:return qsearch(P,a,b,6,ply)
    ms=[];gen(P,ms)
    k=KILL[ply]
    def kf(m):
        s=mvvlva(P,m)
        if m==k:s+=50000
        return -s
    ms.sort(key=kf)
    best=-MATE*2
    n=0
    for m in ms:
        u=make(P,m)
        ks=P.wk if P.stm<0 else P.bk
        if attacked(P,ks,P.stm>0):
            unmake(P,u);continue
        n+=1
        if n==1:sc=-search(P,d-1,-b,-a,ply+1)
        else:
            sc=-search(P,d-1,-a-1,-a,ply+1)
            if a<sc<b:sc=-search(P,d-1,-b,-sc,ply+1)
        unmake(P,u)
        if sc>best:best=sc
        if sc>a:a=sc
        if a>=b:
            if P.b[(m>>7)&127]=='.':KILL[ply]=m
            break
    if n==0:
        ks=P.wk if P.stm>0 else P.bk
        return -MATE+ply if attacked(P,ks,P.stm<0) else 0
    return best
def uci(m):
    f=m&127;t=(m>>7)&127;pr=(m>>14)&7
    return "abcdefgh"[f%10-1]+str(10-f//10)+"abcdefgh"[t%10-1]+str(10-t//10)+("nbrq"[pr-1] if pr else "")
def think(fen,budget=80000):
    global NODES,LIM,TT,KILL
    KILL=[None]*64
    P=parse(fen)
    ms=[];gen(P,ms)
    lg=[]
    for m in ms:
        u=make(P,m)
        ks=P.wk if P.stm<0 else P.bk
        if not attacked(P,ks,P.stm>0):lg.append(m)
        unmake(P,u)
    if not lg:return None
    best=lg[0]
    LIM=budget
    d=1
    while d<=20:
        NODES=0
        sc=-MATE*3;bm=None
        try:
            for i,m in enumerate(lg):
                sn=(P.b[:],P.stm,P.cr,P.ep,P.score,P.wk,P.bk)
                u=make(P,m)
                v=-search(P,d-1,-MATE*2,MATE*2,0)
                unmake(P,u)
                if bm is None or v>sc:sc=v;bm=m
        except Stop:
            P.b[:]=sn[0]
            P.stm,P.cr,P.ep,P.score,P.wk,P.bk=sn[1:]
            break
        if bm is not None:best=bm
        lg.sort(key=lambda m:0 if m==best else 1)
        d+=1
    return uci(best)
def main():
    while True:
        g=post("/game",{})
        if g.get("status")=="done":
            print(json.dumps({k:g.get(k) for k in ("games","wins","draws","losses")}));return
        if g.get("status")!="your_move":continue
        try:u=think(g["fen"])
        except Exception:u=None
        if u is None:post("/resign",{"game":g["game"]});continue
        post("/move",{"game":g["game"],"move":u})
if __name__=="__main__":main()
