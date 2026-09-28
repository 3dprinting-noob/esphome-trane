import pickle, statistics as st
from datetime import datetime
frames,jsons,events=pickle.load(open('cap.pkl','rb'))
def T(h,m): return datetime(2026,9,28,h,m).timestamp()
P={'idle1':(T(10,15),T(10,47)),'cool':(T(11,5),T(11,44)),'idle2':(T(11,50),T(11,57)),'heat':(T(12,10),T(12,58)),'post':(T(13,3),T(13,9))}
def s(cid,fn):
    out=[]
    for k,(a,b) in P.items():
        v=[fn(x[2]) for x in frames.get(cid,[]) if a<=x[0]<=b]
        out.append(f"{k}:{st.median(v):7.0f}[{min(v)},{max(v)}]" if v else f"{k}: -")
    return "  ".join(out)
u=lambda o:(lambda b: b[o]|(b[o+1]<<8) if len(b)>o+1 else -1)
by=lambda o:(lambda b: b[o] if len(b)>o else -1)
for name,cid,fn in [("0x200 u16@0",0x200,u(0)),("0x200 u16@2",0x200,u(2)),("0x200 u16@4",0x200,u(4)),("0x200 u16@6",0x200,u(6)),
  ("0x281 u16@0",0x281,u(0)),("0x281 u16@2",0x281,u(2)),("0x281 b4",0x281,by(4)),("0x281 b5",0x281,by(5)),("0x281 b7",0x281,by(7)),
  ("0x282 b0",0x282,by(0)),("0x282 b2",0x282,by(2)),("0x282 b3",0x282,by(3)),("0x282 b4",0x282,by(4)),
  ("0x2D0 u16@2",0x2D0,u(2)),("0x2D0 u16@4",0x2D0,u(4)),("0x2D1 u16@0",0x2D1,u(0)),("0x2C8 u16@1",0x2C8,u(1)),("0x2D2 u16@0",0x2D2,u(0)),
  ("0x318 u16@4",0x318,u(4)),("0x318 u16@6",0x318,u(6)),("0x384 u16@4",0x384,u(4)),("0x384 u16@6",0x384,u(6)),
  ("0x490 b4",0x490,by(4)),("0x201 b1",0x201,by(1)),("0x201 b2",0x201,by(2)),("0x240 b1",0x240,by(1)),("0x250 b1",0x250,by(1)),("0x331 b4",0x331,by(4)),("0x333 u16@0",0x333,u(0)),("0x420 b4",0x420,by(4)),("0x53E b5",0x53E,by(5))]:
    print(f"{name:12s} {s(cid,fn)}")
