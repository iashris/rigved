import re,json,html
out={}
pat=re.compile(r'<lg xml:id="b(\d\d)_h(\d\d\d)_(\d\d)_(eichler|griffith|vnh|aufrecht)"[^>]*>(.*?)</lg>',re.S)
for b in range(1,11):
  s=open(f'src/vwdata/rigveda/TEI/rv_book_{b:02d}.tei',encoding='utf8').read()
  for m in pat.finditer(s):
    ref=f'{m[1]}.{m[2]}.{m[3]}'
    lines=[html.unescape(re.sub('<[^>]+>','',l)).strip() for l in re.findall(r'<l\b[^>]*>(.*?)</l>',m[5],re.S)]
    out.setdefault(ref,{})[m[4]]=lines
json.dump(out,open('vedaweb_ref.json','w'),ensure_ascii=False)
print(len(out),{k:sum(1 for v in out.values() if k in v) for k in['eichler','griffith','vnh','aufrecht']})
