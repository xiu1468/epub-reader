"""Build examples.tsv (word \t english \t chinese) from Tatoeba zh-en sentence pairs.
Up to N (default 3) different sentences per word, one per line, best first.

Source: npm package tatoeba-sentence-pairs-in-mandarin-chinese-english (sentences.json),
data from https://tatoeba.org (CC BY 2.0 FR). Chinese converted to Traditional with OpenCC s2tw.
Usage: python3 build_examples.py sentences.json dict.tsv forms.tsv [N] > examples.tsv
"""
import json, re, sys
from opencc import OpenCC
cc = OpenCC('s2tw')
sent_path, dict_path, forms_path = sys.argv[1:4]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 3
words = set(l.split('\t', 1)[0].lower() for l in open(dict_path, encoding='utf-8') if l.strip())
forms = dict(l.rstrip('\n').split('\t') for l in open(forms_path, encoding='utf-8') if '\t' in l)
pairs = json.load(open(sent_path, encoding='utf-8'))
BAD = re.compile(r"\b(crap|shit|fuck\w*|damn|bitch|ass|sex\w*|kill\w*|suicide|die[sd]?)\b", re.I)
TOK = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
cands = {}  # lemma -> [(score, en, zh)]
seen = set()
for _, zh, _, en in pairs:
    en = en.strip(); zh = zh.strip()
    if en in seen or not (12 <= len(en) <= 110): continue
    seen.add(en)
    score = abs(len(en) - 45)
    if re.search(r"\b(Tom|Mary|John)\b", en): score += 25
    if BAD.search(en): continue
    raw = TOK.findall(en)
    caps = set(t.lower() for i, t in enumerate(raw) if i > 0 and t[0].isupper())
    toks = set(t.lower() for t in raw)
    for t in toks:
        for lem in {t, forms.get(t)}:
            if lem and lem in words:
                s = score + (0 if t == lem else 30) + (60 if t in caps else 0)
                cands.setdefault(lem, []).append((s, en, zh))
NAMES = re.compile(r"\b(Tom|Mary|John|Ken|Jane|Mike|Bill|Lucy|Jack)\b")
def key(en):  # near-duplicate key: same sentence apart from names / punctuation
    return re.sub(r"[^a-z ]", "", NAMES.sub("X", en).lower()).strip()
best = {}
for lem, lst in cands.items():
    lst.sort(key=lambda x: x[0])
    keep, keys = [], set()
    for s, en, zh in lst:
        k = key(en)
        if k in keys: continue
        keys.add(k); keep.append((en, zh))
        if len(keep) >= N: break
    best[lem] = keep
out = sys.stdout
for w in sorted(best):
    for en, zh in best[w]:
        out.write(f"{w}\t{en.replace(chr(9), ' ')}\t{cc.convert(zh).replace(chr(9), ' ')}\n")
print(len(best), sum(len(v) for v in best.values()), file=sys.stderr)
