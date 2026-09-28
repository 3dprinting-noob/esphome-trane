import pickle, struct, bisect
from datetime import datetime
frames,jsons,events=pickle.load(open('cap.pkl','rb'))
f=lambda b,o: struct.unpack_from('<f',b,o)[0]
u16=lambda b,o: b[o]|(b[o+1]<<8)
hm=lambda t: datetime.fromtimestamp(t).strftime('%H:%M:%S')
def ser(cid,fn): return [(t,fn(b)) for t,_,b in frames[cid]]
def first_nonzero(s,a,b,thr=0.5):
    for t,v in s:
        if a<=t<=b and v>thr: return t
def first_zero(s,a,b):
    for t,v in s:
        if a<=t<=b and v<=0.01: return t
def T(h,m,s=0): return datetime(2026,9,28,h,m,s).timestamp()
sig={'demand 0x281b6':ser(0x281,lambda b:b[6]),'OD fan req 0x281u0':ser(0x281,lambda b:u16(b,0)),'comp req 0x280':ser(0x280,lambda b:f(b,0)),
 'comp act 0x384':ser(0x384,lambda b:f(b,0)),'OD fan act 0x384u6':ser(0x384,lambda b:u16(b,6)),'input W 0x38C':ser(0x38C,lambda b:f(b,4)-30),
 'blower req 0x200u2':ser(0x200,lambda b:u16(b,2)),'blower rpm 0x318u4':ser(0x318,lambda b:u16(b,4)),'blower W 0x320':ser(0x320,lambda b:f(b,0)),
 'static 0x310':ser(0x310,lambda b:f(b,0)*100),'mode 0x281b7':ser(0x281,lambda b:b[7])}
for name,(a,b) in {'cool start':(T(10,57),T(11,2)),'heat start':(T(11,57),T(12,2))}.items():
    print('==',name); r=sorted((first_nonzero(s,a,b) or 9e12,k) for k,s in sig.items())
    for t,k in r: print(' ',hm(t) if t<9e12 else '-',k)
for name,(a,b) in {'cool stop':(T(11,43),T(11,48)),'heat stop':(T(12,59),T(13,4))}.items():
    print('==',name); r=sorted((first_zero(s,a,b) or 9e12,k) for k,s in sig.items())
    for t,k in r: print(' ',hm(t) if t<9e12 else '-',k)
# JSON parse failures
bad=[j for t,c,j in jsons if not isinstance(j,dict)]
print('json not parsed:',len(bad), [str(x)[:60] for x in bad[:3]])
