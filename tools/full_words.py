from pathlib import Path
import pdfplumber,json,re,unicodedata,bisect
base=Path('F:/GRE背单词网站')
result=[]; issues=[]; list_no=1
with pdfplumber.open('F:/GRE/青山学堂GRE全能词.pdf') as pdf:
 for pi,p in enumerate(pdf.pages[5:],6):
    text=p.extract_text() or ''
    m=re.search(r'Word List\s+(\d+)',text)
    if m:list_no=int(m[1])
    headers={w['text']:w['x0'] for w in p.extract_words() if w['text'] in ['单词','音标','词性','释义']}
    if len(headers)<4:
        issues.append({'page':pi,'reason':'headers missing'}); continue
    bounds=sorted(set(round(y,2) for r in p.rects if r['width']>p.width*.75 for y in [r['top'],r['bottom']]))
    bounds+=[p.height-50];bounds=sorted(set(bounds))
    hx=headers['音标'];posx=headers['词性'];meanx=headers['释义']
    # Background rectangle edges delimit complete multi-line entries, even when the headword is centered.
    intervals=[]
    for a,b in zip(bounds,bounds[1:]):
        left=p.crop((20,a,hx-3,b))
        lw=left.extract_words()
        rows=[]
        for w in lw:
            if not re.fullmatch(r'[A-Za-z][A-Za-z\-’\'()/]*',w['text']):continue
            cy=(w['top']+w['bottom'])/2
            if rows and abs(cy-rows[-1][0])<3:rows[-1][1].append(w['text'])
            else:rows.append([cy,[w['text']]])
        if len(rows)>1:
            edges=[a]+[(rows[i][0]+rows[i+1][0])/2 for i in range(len(rows)-1)]+[b]
            intervals.extend(zip(edges,edges[1:]))
        else:intervals.append((a,b))
    for a,b in intervals:
        if b-a<8:continue
        crop=p.crop((20,a,p.width-20,b))
        head=crop.crop((20,a,hx-3,b)).extract_text() or ''
        head=unicodedata.normalize('NFKC',head).strip()
        if not re.fullmatch(r'[A-Za-z][A-Za-z \-’\'()/]*',head) or head in ['Word','List']:continue
        head=re.sub(r'\s+',' ',head).lower()
        defs=crop.crop((posx-2,a,p.width-20,b)).extract_text() or ''
        phon=crop.crop((hx-2,a,posx-3,b)).extract_text() or ''
        if not re.search('[\u4e00-\u9fff]',defs):
            issues.append({'page':pi,'word':head,'reason':'definition missing'});continue
        defs=unicodedata.normalize('NFKC',defs)
        result.append({'word':head,'phonetic':phon.strip(),'base':defs.strip(),'list':list_no,'sources':[{'book':'全能词','page':pi}]})
    if pi%20==0:print(pi,len(result),flush=True)
out=[];seen={}
for x in result:
 if x['word'] in seen:
    prev=seen[x['word']]
    if x['base'] not in prev['base']:prev['base']+='\n'+x['base']
    prev['sources']+=x['sources']
 else:seen[x['word']]=x;out.append(x)
for i,x in enumerate(out):x['id']='w'+str(i+1)
(base/'sources/full-words.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(base/'sources/full-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL',len(result),'UNIQUE',len(out),'ISSUES',issues,flush=True)
