import pickle, struct, bisect
from datetime import datetime
frames,jsons,events=pickle.load(open('cap.pkl','rb'))
f=lambda b,o: struct.unpack_from('<f',b,o)[0]
u16=lambda b,o: b[o]|(b[o+1]<<8)
TS={cid:[x[0] for x in L] for cid,L in frames.items()}
def last(cid,t,fn,lag=0.0):
    i=bisect.bisect_right(TS[cid],t+lag)-1
    return fn(frames[cid][i][2]) if i>=0 else None
hm=lambda t: datetime.fromtimestamp(t).strftime('%H:%M:%S')
def walk(d,path=()):
    for k,v in d.items():
        if isinstance(v,dict): yield from walk(v,path+(k,))
        else: yield path+(k,),v
rows={'E':[],'H':[],'CDP':[],'B':[],'IE':[]}
for t,cid,j in jsons:
    if not isinstance(j,dict): continue
    for p,v in walk(j):
        if p[0]=='SystemOpStatus' and p[-1]=='E': rows['E'].append((t,v))
        if p[0]=='ZoneStatus' and p[-1]=='H' and p[-2]=='1': rows['H'].append((t,v))
        if p[0]=='OdStatus' and p[-1]=='CompDemandPercent': rows['CDP'].append((t,v))
        if p[0]=='OdStatus' and p[-1]=='B': rows['B'].append((t,v))
        if p[0]=='IndoorStatus' and p[-1]=='E': rows['IE'].append((t,v))
print("== SystemOpStatus.E vs outdoor 0x380f1, 0x385f1 ceiling, 0x280 req, 0x490 byte4")
for t,v in rows['E'][::3]:
    print(hm(t), v, round(last(0x380,t,lambda b:f(b,4)),1), round(last(0x385,t,lambda b:f(b,4)),1), round(last(0x280,t,lambda b:f(b,0)),1), last(0x490,t,lambda b:b[4]))
print("== ZoneStatus.1.H vs 0x490 f0 (before and 3s after)")
for t,v in rows['H']: print(hm(t), v, last(0x490,t,lambda b:f(b,0)), last(0x490,t,lambda b:f(b,0),3))
print("== CompDemandPercent vs 0x281 b6 (at +2s)")
m=0;n=0
for t,v in rows['CDP']:
    b6=last(0x281,t,lambda b:b[6],2.5); n+=1; m+= (str(b6)==v)
print(f"match {m}/{n}"); print([ (hm(t),v,last(0x281,t,lambda b:b[6],2.5)) for t,v in rows['CDP'][:8]])
print("== OdStatus.B vs 0x280 f0 req, 0x384 act, 0x385 f1")
for t,v in rows['B'][::6]: print(hm(t), v, round(last(0x280,t,lambda b:f(b,0)),2), round(last(0x384,t,lambda b:f(b,0)),2), round(last(0x385,t,lambda b:f(b,4)),2))
print("== IndoorStatus.E vs 0x200 u16@2, 0x318 u16@4, 0x281 u16@0")
for t,v in rows['IE'][::10]: print(hm(t), v, last(0x200,t,lambda b:u16(b,2),2), last(0x318,t,lambda b:u16(b,4)), last(0x281,t,lambda b:u16(b,0)))
