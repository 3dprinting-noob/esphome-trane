import json, glob, struct, pickle, sys
from datetime import datetime
from collections import defaultdict
frames=defaultdict(list); jsons=[]; events=[]; other=0
for f in sorted(glob.glob(sys.argv[1] + '/*.jsonl' if len(sys.argv) > 1 else 'cap/*.jsonl')):
    for line in open(f):
        r=json.loads(line)
        t=datetime.fromisoformat(r['host_ts']).timestamp()
        ty=r['type']
        if ty=='can':
            frames[r['can_id_int']].append((t,r['device_tick_ms'],bytes.fromhex(r['data'])))
        elif ty=='trane_json':
            jsons.append((t,r.get('can_id'),r.get('json',r.get('json_raw'))))
        elif ty=='collector':
            events.append((r['host_ts'],r['event']))
        else: other+=1
pickle.dump((dict(frames),jsons,events),open('cap.pkl','wb'))
print('events',events)
print('json',len(jsons),'other',other)
print('ids',len(frames))
for cid in sorted(frames):
    l=frames[cid]; dt=(l[-1][0]-l[0][0])/max(len(l)-1,1)
    dl=sorted(set(len(x[2]) for x in l))
    print(f"0x{cid:03X} n={len(l):6d} period={dt:7.2f}s dlc={dl} last={l[-1][2].hex()}")
