import csv,re,json
from opencc import OpenCC
cc=OpenCC('s2tw')
csv.field_size_limit(10**9)
rows=list(csv.DictReader(open('src/ecdict.csv',encoding='utf-8')))
WRE=re.compile(r"^[A-Za-z][A-Za-z'\-]*$")
def num(x):
    try: return int(x)
    except: return 0
LIM=int(__import__('sys').argv[1])
keep={}
for r in rows:
    w=r['word']
    if not WRE.match(w) or not r['translation'].strip(): continue
    b,f=num(r['bnc']),num(r['frq'])
    if (0<b<=LIM) or (0<f<=LIM) or num(r['collins'])>0 or r['oxford']=='1' or r['tag'].strip():
        keep[w.lower()]=r
# forms map
forms={}
for r in rows:
    w=r['word'].lower()
    ex=r['exchange']
    if not ex: continue
    parts=dict(p.split(':',1) for p in ex.split('/') if ':' in p)
    if '0' in parts and parts['0'].lower() in keep and w!=parts['0'].lower() and WRE.match(w):
        forms.setdefault(w,parts['0'].lower())
    if w in keep:
        for k in 'pdi3rts':
            if k in parts:
                for f in parts[k].split(','):
                    f=f.lower()
                    if f!=w and WRE.match(f): forms.setdefault(f,w)
def clean(t):
    lines=[l.strip() for l in t.replace('\\n','\n').split('\n') if l.strip()]
    main=[l for l in lines if not l.startswith('[')]
    if not main: main=lines[:1]
    out=cc.convert(' | '.join(main[:5]))
    return out.replace('\t',' ')
out=[]
for w,r in sorted(keep.items()):
    c=num(r['collins']); rank=num(r['frq']) or num(r['bnc'])  # COCA rank, fall back to BNC
    out.append(f"{r['word']}\t{r['phonetic'].replace(chr(9),' ')}\t{clean(r['translation'])}\t{c or ''}\t{rank or ''}")
open('dict.tsv','w').write('\n'.join(out)+'\n')
open('forms.tsv','w').write('\n'.join(f"{a}\t{b}" for a,b in sorted(forms.items()))+'\n')
print(len(keep), len(forms))
