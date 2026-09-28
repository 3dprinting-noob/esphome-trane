import pickle, struct, statistics as st
from datetime import datetime
frames,jsons,events=pickle.load(open('cap.pkl','rb'))
f=lambda b,o: struct.unpack_from('<f',b,o)[0]
def T(h,m): return datetime(2026,9,28,h,m).timestamp()
P={'idle1':(T(10,15),T(10,47)),'cool':(T(11,5),T(11,44)),'idle2':(T(11,50),T(11,57)),'heat':(T(12,10),T(12,58)),'post':(T(13,3),T(13,9))}
def stats(cid,o):
    out=[]
    for k,(a,b) in P.items():
        v=[f(x[2],o) for x in frames.get(cid,[]) if a<=x[0]<=b and len(x[2])>=o+4]
        v=[x for x in v if x==x and abs(x)<1e7]
        out.append(f"{k}:{st.median(v):8.2f}[{min(v):.1f},{max(v):.1f}]" if v else f"{k}:   -")
    return "  ".join(out)
for cid in [0x283,0x2C0,0x310,0x380,0x381,0x382,0x383,0x385,0x386,0x387,0x388,0x389,0x38C,0x38F,0x3D0,0x410,0x430,0x450,0x460,0x4B2,0x490,0x491]:
    for o in (0,4):
        L=frames.get(cid,[])
        if L and len(L[0][2])>=o+4: print(f"0x{cid:03X} f{o//4}  {stats(cid,o)}")
