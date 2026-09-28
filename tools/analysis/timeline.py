import pickle, struct, time
from datetime import datetime
frames,jsons,events=pickle.load(open('cap.pkl','rb'))
f=lambda b,o: struct.unpack_from('<f',b,o)[0]
u16=lambda b,o: b[o]|(b[o+1]<<8)
def series(cid, fn):
    return [(t,fn(b)) for t,_,b in frames.get(cid,[]) if len(b)>=1]
S={
 'req':series(0x280,lambda b:f(b,0)),
 'act':series(0x384,lambda b:f(b,0)),
 'dem':series(0x281,lambda b:b[6]),
 'blw':series(0x281,lambda b:b[7]),
 'ret':series(0x308,lambda b:f(b,0)),
 'sup':series(0x308,lambda b:f(b,4)),
 'Ps':series(0x383,lambda b:f(b,0)),
 'Pl':series(0x383,lambda b:f(b,4)),
 'kW':series(0x385,lambda b:f(b,0)),
 'inW':series(0x38C,lambda b:f(b,4)),
 'fan':series(0x384,lambda b:u16(b,6)),
 'stat':series(0x282,lambda b:b[1]),
 'bspd':series(0x318,lambda b:u16(b,4)),
 'bW':series(0x320,lambda b:f(b,0)),
 'sp':series(0x310,lambda b:f(b,0)),
 'room':series(0x490,lambda b:f(b,0)),
 'out':series(0x380,lambda b:f(b,4)),
 'dis':series(0x381,lambda b:f(b,4)),
}
t0=min(v[0][0] for v in S.values() if v); t1=max(v[-1][0] for v in S.values() if v)
import bisect
def at(k,t):
    v=S[k]; ts=[x[0] for x in v]
    if not v: return None
    i=bisect.bisect_right(ts,t)-1
    return v[max(i,0)][1]
keys=list(S)
print("time  "+" ".join(f"{k:>6}" for k in keys))
t=t0
while t<=t1:
    row=[]
    for k in keys:
        v=at(k,t); row.append(f"{v:6.1f}" if isinstance(v,float) else f"{v!s:>6}")
    print(datetime.fromtimestamp(t).strftime('%H:%M')+" "+" ".join(row))
    t+=120
