from pathlib import Path
import json
from pypdf import PdfReader

base = Path('F:/GRE背单词网站')
names = ['青山学堂GRE全能词','青山学堂GRE词表-精准释义V1.0','青山学堂GRE词表-熟词僻义V1.0','青山学堂GRE词表-等价词对V2.0','真经GRE等价词汇总']
for name in names:
    r = PdfReader(Path('F:/GRE') / (name + '.pdf'))
    pages = [p.extract_text(extraction_mode='layout') for p in r.pages]
    (base/'sources'/(name+'.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
    (base/'sources'/(name+'.txt')).write_text('\n'.join(f'\n=== PAGE {i+1} ===\n{p}' for i,p in enumerate(pages)),encoding='utf-8')
    print(name, 'pages',len(pages),'chars',sum(map(len,pages)),flush=True)
    print('\n'.join(pages[1 if len(pages)>1 else 0].splitlines()[:30]),flush=True)
