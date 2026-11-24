import json,re,unicodedata,difflib,collections
ref=json.load(open('vedaweb_ref.json'))
ours=json.load(open('/Users/iashris/Desktop/rigved/public/data/vedas/rigveda.json'))
def fold(s):
  s=unicodedata.normalize('NFD',s.lower());s=''.join(c for c in s if not unicodedata.combining(c))
  s=s.replace('sh','s').replace('ri','r');return re.sub('[^a-z]','',s)
okey=lambda r:f"{r['mandala']:02d}.{r['hymn']:03d}.{r['verse']:02d}"
bym=collections.defaultdict(list)
for r in ours: r['_k']=okey(r);r['_f']=fold(r['text']);bym[r['mandala']].append(r)
exact=collections.defaultdict(list)
for r in ours: exact[(r['mandala'],r['_f'])].append(r)
assign={};how=collections.Counter()
for k in sorted(ref):
  m,h,v=map(int,k.split('.'));g=' '.join(ref[k]['griffith']);fg=fold(g)
  c=exact.get((m,fg))
  if c:
    best=min(c,key=lambda r:abs(r['hymn']-h)*100+abs(r['verse']-v));assign[k]=(best['_k'],1.0);how['exact']+=1;continue
  cands=[r for r in bym[m] if abs(r['hymn']-h)<=12]
  sm=difflib.SequenceMatcher(None,autojunk=False);sm.set_seq2(fg);best=None;br=0
  for r in cands:
    sm.set_seq1(r['_f'])
    if sm.real_quick_ratio()<=br or sm.quick_ratio()<=br: continue
    x=sm.ratio()
    if x>br: br,best=x,r
  assign[k]=(best['_k'] if best else None,br);how['fuzzy>=.9' if br>=.9 else 'fuzzy.75-.9' if br>=.75 else 'nomatch']+=1
json.dump(assign,open('assign.json','w'))
print(how)
used=collections.Counter(a for a,b in assign.values() if b>=.9 and a)
print('our rows used >1:',[(k,n) for k,n in used.items() if n>1][:30])
print('our rows unused:',len(set(r['_k'] for r in ours)-set(used)))
moved=[(k,a) for k,(a,b) in assign.items() if b>=.9 and a!=k];print('moved',len(moved),collections.Counter(k[:2] for k,a in moved))
