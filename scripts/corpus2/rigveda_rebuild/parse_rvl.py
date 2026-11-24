import re,glob,json,html
out={}
for p in sorted(glob.glob('src/rvlinks/rvhymns/rv*.html')):
  s=open(p,encoding='utf8').read()
  for blk in re.split(r"<a id='rv",s)[1:]:
    m=re.match(r"(\d\d)\.(\d\d\d)\.(\d\d)'",blk)
    if not m: continue
    k=f'{m[1]}.{m[2]}.{m[3]}'
    g=lambda c:(re.search(rf'<p class="{c}">(.*?)</p>',blk,re.S) or [None,''])[1]
    clean=lambda t:re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t))).strip()
    out[k]={'en':clean(g('en')),'sa':clean(g('sa'))}
json.dump(out,open('rvlinks_ref.json','w'),ensure_ascii=False)
print(len(out),sum(1 for v in out.values() if v['en']),sum(1 for v in out.values() if v['sa']))
for k in ['01.065.01','01.065.02','01.058.01','08.049.01']: print(k,out[k]['en'][:160])
