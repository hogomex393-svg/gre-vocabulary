from pathlib import Path
import json
base=Path('F:/GRE背单词网站/sources')
def load(tag):return json.loads((base/f'{tag}-rows.json').read_text(encoding='utf8'))
def save(tag,rows):(base/f'{tag}-rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
rows=load('rare')
rows=[r for r in rows if r['page']!=5]
for a,b,c in [('shoulder','n. 肩膀','v. 承担'),('particular','adj. 特别的，不寻常的','n. 细节，详情'),('want','v. 想','v. 缺乏'),('wealth','n. 财富','n. 大量，丰富'),('issue','n. 论文','v. 宣布'),('issue','n. 问题','v. 发起')]:rows.append({'cols':[a,b,c],'page':5,'confidence':1,'verified':True})
for r in rows:
 if r['cols'][0]=='discount':r['cols'][2]='v. 认为……不重要，低估'
 if r['cols'][0]=='eclipse':r['cols'][2]='v. 使……黯然失色'
 if r['cols'][0]=='inform':r['cols'][2]='v. 对……有影响'
 if r['cols'][0]=='contradict':r['cols'][1]='v. 与……矛盾'
 if r['cols'][0]=='mirror':r['cols'][2]='v. 与……相似'
save('rare',rows)
rows=load('precise')
for r in rows:
 if r['cols'][0]=='resonate':r['cols'][2]='v. 与……的想法共鸣；与现实共鸣'
 if r['cols'][0]=='descriptivescience':r['cols'][0]='descriptive science'
 if r['cols'][0]=='empiricial':r['cols'][0]='empirical'
save('precise',rows)
rows=load('pairs')
for r in rows:
 if r['cols'][0]=='opprobrium' and r['cols'][1]=='vituperation':r['cols'][2]='谩骂'
 if r['cols'][0]=='reverence' and r['cols'][1]=='veneration':r['cols'][2]='尊重'
 fixes={'accession to':['accession to','acquiescence to','同意'],'immaterial':['immaterial','inconsequential','不重要的'],'impair':['impair','undermine','削弱'],'meticulousness':['meticulousness','scrupulousness','一丝不苟'],'omnivorous':['omnivorous','undiscriminating','不挑食的'],'predilection for':['predilection for','proclivity toward','倾向'],'splendor':['splendor','sumptuousness','华丽'],'1qnop':['doubt','reservation','怀疑，保留意见']}
 if r['cols'][0] in fixes and (not r['cols'][2] or r['cols'][0]=='1qnop'):r['cols']=fixes[r['cols'][0]];r['confidence']=1;r['verified']=True
 for i in range(3):
  r['cols'][i]=r['cols'][i].replace('.......','……').replace('......·','……').replace('....·','……').replace('....','……').replace('宣告.·....·','宣告……')
save('pairs',rows)
