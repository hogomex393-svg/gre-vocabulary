from pathlib import Path
import json,time,urllib.request,shutil
b=Path('F:/GRE背单词网站')
current=json.load(urllib.request.urlopen('http://127.0.0.1:18765/api/state'))['state']
clean=json.loads((b/'tools/初始空白存档.json').read_text(encoding='utf8'));clean['updated']=int(time.time()*1000)
req=urllib.request.Request('http://127.0.0.1:18765/api/state',data=json.dumps({'state':clean,'revision':current['revision']}).encode(),headers={'Content-Type':'application/json'},method='PUT')
result=json.load(urllib.request.urlopen(req));stored=json.load(urllib.request.urlopen('http://127.0.0.1:18765/api/state'))['state']
assert stored['activeDay']==0 and not stored['days']['0']['words']['learned'] and not stored['days']['0']['words']['match']
assert not stored['mistakes']['words'] and stored['resume'] is None
for p in (b/'存档').glob('*.json'):
 if p.name!='学习进度.json':shutil.copyfile(b/'存档/学习进度.json',p)
record=json.loads((b/'tools/验证结果.json').read_text(encoding='utf8'))
record['browserChecks']=['翻卡确认后重开恢复到下一个词','答错不计通过并显示原书解释','连连看正确配对刷新后仍为1/30','30/30/30/10分组','六选二选两个正确答案后计进度','双向搭档只完成一个方向重开后为99待练且0掌握','无效存档拒绝不覆盖','恢复有效存档并备份当前文件','375px首页与连连看无页面横向溢出','1280px四组卡片布局','第30天100词与50组，显示新词/复习标记','启动入口从服务关闭状态成功启动','WebMCP读取、打开浏览、拒绝无效搭档操作']
record['handoff']='已清除测试进度，从第1天开始；服务保持运行'
(b/'tools/验证结果.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print('Ready: day 1, 100 words / 50 pairs, no test progress')
