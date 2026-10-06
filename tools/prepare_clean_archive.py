from pathlib import Path
import json,time,urllib.request
b=Path('F:/GRE背单词网站')
current=json.load(urllib.request.urlopen('http://127.0.0.1:18765/api/state'))['state']
(b/'tools/界面验证用进度.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf8')
def record(extra):return {'learned':{},'quiz':{},extra:{},'stats':{},'cursor':{}}
clean={'version':1,'activeDay':0,'updated':int(time.time()*1000),'days':{'0':{'started':'2026/10/6','words':record('match'),'pairs':record('pair')}},'mistakes':{'words':{},'pairs':{}},'resume':None}
(b/'tools/初始空白存档.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2),encoding='utf8')
(b/'tools/无效存档测试.json').write_text('{"version":0}',encoding='utf8')
