"""Build examples.tsv (word \t english \t chinese) from Tatoeba zh-en sentence pairs.

Source: npm package tatoeba-sentence-pairs-in-mandarin-chinese-english (sentences.json),
data from https://tatoeba.org (CC BY 2.0 FR). Chinese converted to Traditional with OpenCC s2tw.
Usage: python3 build_examples.py sentences.json dict.tsv forms.tsv > examples.tsv
"""
import json, re, sys
from opencc import OpenCC
cc = OpenCC('s2tw')
sent_path, dict_path, forms_path = sys.argv[1:4]
words = set(l.split('\t', 1)[0].lower() for l in open(dict_path, encoding='utf-8') if l.strip())
forms = dict(l.rstrip('\n').split('\t') for l in open(forms_path, encoding='utf-8') if '\t' in l)
pairs = json.load(open(sent_path, encoding='utf-8'))
BAD = re.compile(r"\b(crap|shit|fuck\w*|damn|bitch|ass|sex\w*|kill\w*|suicide|die[sd]?)\b", re.I)
TOK = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
best = {}  # lemma -> (score, en, zh)
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
                if lem not in best or s < best[lem][0]:
                    best[lem] = (s, en, zh)
out = sys.stdout
for w in sorted(best):
    _, en, zh = best[w]
    out.write(f"{w}\t{en.replace(chr(9), ' ')}\t{cc.convert(zh).replace(chr(9), ' ')}\n")
print(len(best), file=sys.stderr)
