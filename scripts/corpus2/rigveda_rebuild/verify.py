import json,re,unicodedata,collections,sys
sys.path.insert(0,'.')
new=json.load(open('rigveda.new.json'));ref=json.load(open('vedaweb_ref.json'))
jb=json.load(open('/Users/iashris/Desktop/rigved/public/data/vedas/rigveda_jamison_brereton.json'))
print('refs == J&B refs:', [r['reference'] for r in new]==sorted(r['reference'] for r in jb) and len(set(r['reference'] for r in new))==10552)
print('ellipses left:', sum('...' in r['meaning'] or '…' in r['meaning'] or '...' in r['text'] for r in new))
print('empty text:', sum(not r['text'].strip() for r in new), 'empty skt:', sum(not r['meaning'].strip() for r in new))
# Eichler vs Aufrecht: transliterate Devanagari -> ISO, compare de-accented letters
from indic_transliteration import sanscript
def iso_fold(s):
  s=unicodedata.normalize('NFD',s.lower());s=''.join(c for c in s if not unicodedata.combining(c));return re.sub('[^a-z]','',s)
bad=[]
for r in new:
  d=sanscript.transliterate(r['meaning'],sanscript.DEVANAGARI,sanscript.ISO)
  a=' '.join(ref[r['reference']]['aufrecht'])
  if iso_fold(d)!=iso_fold(a): bad.append((r['reference'],iso_fold(d),iso_fold(a)))
print('Eichler≠Aufrecht (letters only):',len(bad))
import difflib
c=collections.Counter()
for k,x,y in bad:
  for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,x,y,autojunk=False).get_opcodes():
    if op!='equal': c[(x[i1:i2],y[j1:j2])]+=1
print(c.most_common(25))
json.dump(bad,open('eichler_vs_aufrecht.json','w'),ensure_ascii=False)
