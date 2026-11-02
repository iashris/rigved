import json, os, re, sys, functools
import pathlib; root=str(pathlib.Path(__file__).resolve().parents[2]/'public'/'data')
files={}
for d,_,fs in os.walk(root):
    for f in fs:
        if f.endswith('.json'): files[f[:-5]]=os.path.join(d,f)
@functools.lru_cache(None)
def load(t): return json.load(open(files[t]))
def norm(r): return '.'.join(str(int(p)) if p.isdigit() else p for p in re.split('[.:]',str(r)))
def kw(pattern, texts, limit=6, width=150):
    rx=re.compile(pattern)
    for t in texts:
        n=0
        for e in load(t):
            s=e.get('text') or ''
            m=rx.search(s)
            if m:
                a=max(0,m.start()-40); print(f"  {t} {e['reference']}: …{s[a:a+width]}…".replace('\n',' '))
                n+=1
                if n>=limit: break
def vr(t, a, b=None, width=130):
    ents=load(t); b=b or a
    ia=next((i for i,e in enumerate(ents) if norm(e['reference'])==norm(a)),None)
    ib=next((i for i,e in enumerate(ents) if norm(e['reference'])==norm(b)),None)
    if ia is None or ib is None: print(f"!! {t} {a}..{b}: NOT FOUND ({ia},{ib})"); return
    sl=ents[ia:ib+1]; print(f"== {t} {a}..{b}: {len(sl)} entries, {sum(len(e.get('text') or '') for e in sl)} chars")
    for e in sl:
        s=(e.get('text') or '').replace('\n',' ')
        tr='' if re.search(r'[.!?;:)"\'’”\]]\s*$',s) else ' [TRUNC]'
        print(f"  [{e['reference']}] {s[:width]}{tr}")
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='kw': kw(sys.argv[2], sys.argv[3].split(','), int(sys.argv[4]) if len(sys.argv)>4 else 6)
    else: vr(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv)>4 else None, int(sys.argv[5]) if len(sys.argv)>5 else 130)
