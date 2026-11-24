import json,re,unicodedata,collections,difflib
ref=json.load(open('vedaweb_ref.json'));assign=json.load(open('assign.json'))
rvl=json.load(open('rvlinks_ref.json'))
oldl=json.load(open('/Users/iashris/Desktop/rigved/public/data/vedas/rigveda.json'))
ours={f"{r['mandala']:02d}.{r['hymn']:03d}.{r['verse']:02d}":r for r in oldl}
W=re.compile(r"[^\W\d_]+(?:[̀-ͯ][^\W\d_]*)*",re.U)
def words(s): return W.findall(unicodedata.normalize('NFC',s))
# learn VW->ours word map from aligned exact rows
pairs=collections.defaultdict(collections.Counter)
for k,(o,b) in assign.items():
  if b<1.0: continue
  a=words(ours[o]['text']);g=words(' '.join(ref[k]['griffith']))
  if len(a)!=len(g): continue
  for x,y in zip(g,a):
    if x!=y: pairs[x][y]+=1
def fold(w):
  w=unicodedata.normalize('NFD',w.lower());w=''.join(ch for ch in w if not unicodedata.combining(ch));return w.replace('sh','s').replace('ri','r')
wmap={}
for x,c in pairs.items():
  y,n=c.most_common(1)[0]
  if fold(x)==fold(y) and (n>=2 or len(c)==1): wmap[x]=y
def conv(s):
  s=unicodedata.normalize('NFC',s)
  s=W.sub(lambda m: wmap.get(m.group(0), m.group(0)),s)
  # residual Griffith-style vowels
  for a,b in [('â','ā'),('î','ī'),('û','ū'),('Â','Ā'),('Î','Ī'),('Û','Ū'),('r̥i','ṛ'),('R̥i','Ṛ')]: s=s.replace(a,b)
  for a,b in [('Anṣumatīs','Aṃśumatīs'),('Riksha','Ṛkṣa'),('Pṛshadvāna','Pṛṣadvāna')]: s=s.replace(a,b)
  s=re.sub(r'(?<=[a-z,;] )In\b','in',s)
  return s
def FOLD(t):
  t=unicodedata.normalize('NFD',t.lower());t=''.join(c for c in t if not unicodedata.combining(c));return re.sub('[^a-z]','',t.replace('sh','s').replace('ri','r'))
ACC=re.compile('[॑-॔᳐-᳿꣠-ꣿ]')
out=[];prov={};resid=collections.Counter()
for k in sorted(ref):
  m,h,v=map(int,k.split('.'))
  ei=[unicodedata.normalize('NFC',l) for l in ref[k]['eichler']]
  acc=' । '.join(ei)+' ॥'; plain=ACC.sub('',acc)
  o,b=assign[k]
  if o and b>=.9: text=ours[o]['text']; src='site-griffith' if o==k else f'site-griffith-moved-from-{o}'
  else:
    vw=' '.join(ref[k]['griffith']); fvw=FOLD(vw); text=vw; src='vedaweb-griffith'
    if not (m==1 and 65<=h<=70):
      cands=[]
      if k in ours: cands.append((ours[k]['text'],'site-griffith-completed'))
      rt=rvl[k]['en']
      if rt and rt!='-en-': cands.append((rt,'rvlinks-griffith'))
      cands=[(t,sname) for t,sname in cands if fvw in FOLD(t) and len(FOLD(t))>len(fvw)+10]
      if cands: text,src=max(cands,key=lambda c:len(c[0]))
      elif rt and rt!='-en-' and FOLD(rt)!=fvw: src='vedaweb-griffith(rvlinks-differs)'
    if src!='site-griffith-completed': text=conv(text)
    for w in words(text):
      if re.search('[âîûṣ]|r̥|sh',w): resid[w]+=1
  if k=='08.100.04': text=conv(rvl[k]['en'].replace('existeth 1 surpass','existeth I surpass')); src='rvlinks-griffith(ocr-fixed)'
  out.append({'reference':k,'text':text,'mandala':m,'hymn':h,'verse':v,'meaning':plain,'meaning_accented':acc,'vedaId':'rigveda'})
  prov[k]=src
json.dump(out,open('rigveda.new.json','w'),ensure_ascii=False,indent=1)
json.dump(prov,open('provenance.json','w'),indent=0)
print(len(out),collections.Counter(p.split('-from')[0] for p in prov.values()));print('residual old-style words in fallback:',resid.most_common(40))
