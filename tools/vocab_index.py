#!/usr/bin/env python3
"""Rebuild vocab/books.json from vocab/books/*.json and check every book file.

Usage: python3 tools/vocab_index.py   (run from the repo root)
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'vocab'
CATS = {'chunk', 'word', 'pattern'}
FIELDS = ('n', 'cat', 'term', 'ipa', 'pos', 'meaning', 'usage', 'example', 'trans')

index, errors = [], []
for f in sorted((ROOT / 'books').glob('*.json')):
    b = json.loads(f.read_text(encoding='utf-8'))
    expect = 1
    for seg in b['segments']:
        for it in seg['items']:
            missing = [k for k in FIELDS if k not in it]
            if missing: errors.append(f'{f.name} #{it.get("n")}: missing {missing}')
            if it.get('cat') not in CATS: errors.append(f'{f.name} #{it.get("n")}: bad cat {it.get("cat")}')
            if it.get('n') != expect: errors.append(f'{f.name}: expected #{expect}, got #{it.get("n")}')
            expect = it.get('n', expect) + 1
        nums = {it['n'] for it in seg['items']}
        for n in seg.get('top', []):
            if n not in nums: errors.append(f'{f.name} seg {seg["seg"]}: top #{n} not in segment')
    index.append({'id': b['id'], 'title': b['title'], 'created': b.get('created', ''),
                  'file': f.name, 'segments': len(b['segments']), 'count': expect - 1})

if errors:
    print('\n'.join(errors)); sys.exit(1)
(ROOT / 'books.json').write_text(json.dumps(index, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
for b in index: print(f'{b["file"]}: {b["segments"]} 段, #1–#{b["count"]}')
