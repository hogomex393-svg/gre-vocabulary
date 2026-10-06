from pathlib import Path
import json,re,difflib
b=Path('F:/GRE背单词网站/sources')
rows=json.loads((b/'pairs-rows.json').read_text(encoding='utf8'))
bad=[r for r in rows if not (re.fullmatch(r'[A-Za-z][A-Za-z \-\'()]*',r['cols'][0]) and re.fullmatch(r'[A-Za-z][A-Za-z \-\'()]*',r['cols'][1]) and re.search('[\u4e00-\u9fff]',r['cols'][2]))]
print('SKIPPED',json.dumps(bad,ensure_ascii=False))
d=json.loads((b/'dataset.json').read_text(encoding='utf8'));dictionary={x['word'] for x in d['words']}
scanned={w for r in rows for w in r['cols'][:2]}
zhen={w for x in d['pairs'] if any(s['book']=='真经等价词' for s in x['sources']) for w in x['words']}
dictionary|=zhen
print('SUSPECT SCAN',[(w,difflib.get_close_matches(w,dictionary,1,.87)) for w in sorted(scanned) if w not in dictionary and difflib.get_close_matches(w,dictionary,1,.87)])
print('SHORT/MALFORMED',[(x['words'],x['meaning']) for x in d['pairs'] if any(len(w)<3 or re.search(r'[0-9.;:/]',w) for w in x['words'])])
print('SCANNED ROWS',len(rows),'VALID',len(rows)-len(bad))
