from pathlib import Path
import json,re,unicodedata
base=Path('F:/GRE背单词网站')
def norm(t):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',t)).strip()
spellings={'empiricial':'empirical','prodigial':'prodigal','revivial':'revival','hierachical':'hierarchical','unostentious':'unostentatious'}
phrases={'ntantamountto':'tantamount to','insulatedfrom':'insulated from','bufferedagainst':'buffered against','hewto':'hew to','conformto':'conform to','squarewith':'square with','interestedin':'interested in','drawnto':'drawn to','drawout':'draw out','inferablefrom':'inferable from','entailedby':'entailed by','attributedto':'attributed to','explainedby':'explained by','staveoff':'stave off','cedeto':'cede to','leftto':'left to','liberationfrom':'liberation from','guardedwith':'guarded with','stintingwith':'stinting with','ruleout':'rule out','stripaway':'strip away','ringtrue':'ring true','shrugoff':'shrug off'}
def word(t):
 t=norm(t).lower().replace('’',"'")
 return phrases.get(t,spellings.get(t,t))
words=json.loads((base/'sources/full-words.json').read_text(encoding='utf8'))
wm={x['word']:x for x in words}; audit=[];supplements={}
for tag,book in [('precise','精准释义'),('rare','熟词僻义')]:
 path=base/'sources'/f'{tag}-rows.json'
 if not path.exists():continue
 rows=json.loads(path.read_text(encoding='utf8'))
 for row in rows:
    a,b,c=map(norm,row['cols']); a=word(a)
    if not re.fullmatch(r'[a-z][a-z \-\'()]*',a):continue
    if not c: audit.append({'kind':tag,**row});continue
    if a not in wm:
        x={'id':'w'+str(len(words)+1),'word':a,'base':b or c,'phonetic':'','list':None,'sources':[]};words.append(x);wm[a]=x
    x=wm[a]; x.setdefault(tag,[])
    x.setdefault('common',[])
    if b and b not in x['common']:x['common'].append(b)
    if c not in x[tag]:x[tag].append(c)
    x['sources'].append({'book':book,'page':row['page']})
    if row['confidence']<.86:audit.append({'kind':tag,**row})
    supplements[tag]=supplements.get(tag,0)+1
pairs=[];pm={};counts={'青山等价词':0,'真经等价词':0};dup=0
def add(a,b,meaning,book,page,confidence=1):
 global dup
 a,b=word(a),word(b)
 if a==b or not a or not b:return
 key='|'.join(sorted([a,b])); src={'book':book,'page':page}
 if key in pm:
    x=pm[key];dup+=1
    if meaning not in x['meanings']:x['meanings'].append(meaning)
    if src not in x['sources']:x['sources'].append(src)
 else:
    x={'id':'p'+str(len(pairs)+1),'words':[a,b],'meanings':[meaning],'sources':[src]};pairs.append(x);pm[key]=x
 counts[book]+=1
 if confidence<.86:audit.append({'kind':'pair','words':[a,b],'meaning':meaning,'page':page,'confidence':confidence})
path=base/'sources/pairs-rows.json'
if path.exists():
 for row in json.loads(path.read_text(encoding='utf8')):
    a,b,c=map(norm,row['cols'])
    if re.fullmatch(r'[A-Za-z][A-Za-z \-\'()]*',a) and re.fullmatch(r'[A-Za-z][A-Za-z \-\'()]*',b) and re.search('[\u4e00-\u9fff]',c):add(a,b,c,'青山等价词',row['page'],row['confidence'])
pages=json.loads((base/'sources/真经GRE等价词汇总.json').read_text(encoding='utf8'))
for pi,text in enumerate(pages,1):
 current=None
 for line in text.splitlines():
    cols=re.split(r'\s{2,}',line.strip())
    if len(cols)>=3 and re.fullmatch(r'[A-Za-z][A-Za-z \-\'().]*',cols[0]) and re.search('[\u4e00-\u9fff]',cols[-1]):
        a=cols[0]; bs=','.join(cols[1:-1]); meaning=cols[-1]
        current=(a,bs,meaning)
        for b in re.split('[,，、]',bs):add(a,b,meaning,'真经等价词',pi)
    elif current and len(cols)==1 and re.search('[\u4e00-\u9fff]',cols[0]) and len(cols[0])<35:
        # preserve wrapped Chinese explanations on the original row
        a,bs,meaning=current;meaning+=cols[0];current=(a,bs,meaning)
        for b in re.split('[,，、]',bs):
            key='|'.join(sorted([word(a),word(b)]))
            if key in pm:pm[key]['meanings'][-1]=meaning
for x in words:
 x['meaning']='；'.join(x.get('precise',[])) or '；'.join(x.get('rare',[])) or x['base']
 x['short']=re.sub(r'^(adj|adv|vt|vi|v|n)\.?\s*','',x['meaning'],flags=re.I).replace('\n','；')
for x in pairs:x['meaning']='；'.join(x['meanings'])
context_senses={('anonymous','obscure'):'不出名的',('obfuscate','obscure'):'使……难懂',('obscure','opaque'):'不透明的；难懂的',('antagonistic','inimical'):'敌对的，不友好的',('deleterious','inimical'):'有害的',('camouflage','mimic'):'和……相似',('mimic','replicate'):'模仿',('conceivable','plausible'):'看似合理的，可能的',('confound','flummox'):'使困惑',('confound','perplex'):'使困惑',('confound','resist'):'挫败',('blemish','defect'):'缺点，污点'}
for x in pairs:
 key=tuple(sorted(x['words']))
 if key in context_senses:x['meaning']=context_senses[key];x['contextNote']='多义词组已按此词对的对应义项练习；原表完整释义仍保留。'
data={'words':words,'pairs':pairs,'meta':{'counts':counts,'duplicatesMerged':dup,'supplements':supplements,'wordCount':len(words),'pairCount':len(pairs),'built':'2026-10-06','merge':'按无序词对去重，保留不同释义和来源，不做传递合并','normalizedSpellings':spellings,'normalizedPhrases':phrases}}
(base/'dist/data.js').write_text('window.GRE_DATA = '+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf8')
(base/'sources/audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
(base/'sources/dataset.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(data['meta'],ensure_ascii=False),flush=True);print('audit',len(audit),flush=True)
