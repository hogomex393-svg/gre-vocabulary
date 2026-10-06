import pdfplumber,json,re,unicodedata
from pathlib import Path
base=Path('F:/GRE背单词网站/sources')
data=json.loads((base/'full-words.json').read_text(encoding='utf8'));seen={x['word'] for x in data};missing=[];counts={}
with pdfplumber.open('F:/GRE/青山学堂GRE全能词.pdf') as pdf:
 for pi,p in enumerate(pdf.pages[5:],6):
    ws=p.extract_words();headers={w['text']:w['x0'] for w in ws if w['text'] in ['单词','音标','词性','释义']}
    hx=headers.get('音标',140)
    column=p.crop((20,100,hx-3,p.height-50)).extract_text() or ''
    for head in column.splitlines():
       head=unicodedata.normalize('NFKC',head).lower().strip()
       if re.fullmatch(r'[a-z][a-z \-’\'()/]*',head):
          counts[pi]=counts.get(pi,0)+1
          if head not in seen:missing.append({'page':pi,'word':head})
print('HEADS',sum(counts.values()),'EXTRACTED',len(data),'MISSING',missing)
(base/'coverage.json').write_text(json.dumps({'headCount':sum(counts.values()),'missing':missing,'pages':counts},ensure_ascii=False,indent=2),encoding='utf8')
print('LIST COUNTS', {n:sum(x['list']==n for x in data) for n in range(1,29)})
