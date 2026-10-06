from pathlib import Path
import json
b=Path('F:/GRE背单词网站')
p=b/'dist/app.js';s=p.read_text(encoding='utf8')
s=s.replace('· 随时停下，下次接着背。','· 随时停下，下次接着背。')
s=s.replace("${isWord?'全能词 · 分四次背完':'等价词 · 分五组记牢'}", "${isWord?'全能词 · 分四次背完':'等价词 · 分五组记牢'}")
s=s.replace("<span class=\"muted\">${learned} / ${list.length} ${isWord?'词':'组'}</span>","<span class=\"muted\">${planText(book)} · ${learned} / ${list.length} ${isWord?'词':'组'}</span>")
s=s.replace('最后一天按词库剩余数量安排。','新词不足时以已学词补足每日额度，并标记为复习。')
s=s.replace('<h3>全能词 · 完整释义</h3>',"<h3>${x.list?'全能词 · 完整释义':'补充词条 · 常见释义'}</h3>")
s=s.replace("${sources(x)}</div>`;}\nfunction start", "${x.common?.length?'<h3>补充资料中的常见义 · 对照</h3><p>'+escape(x.common.join('；'))+'</p>':''}${sources(x)}</div>`;}\nfunction start")
s=s.replace("<p>${escape(x.meaning)}</p><p class=\"pair-hint\">", "<p>${escape(x.meaning)}</p>${x.contextNote?'<h3>原表完整释义</h3><p>'+escape(x.meanings.join('；'))+'</p>':''}<p class=\"pair-hint\">")
s=s.replace('打开原 PDF 的链接依赖 F:\\GRE 中的原始资料。词库本身已包含在网站内，背诵时无需联网。','原 PDF 副本保存在本文件夹“资料原件”目录中，背诵和查阅均无需联网。')
p.write_text(s,encoding='utf8')
p=b/'使用说明.md';s=p.read_text(encoding='utf8');s=s.replace('也可以用顶部选择框回到以前的学习日。','也可以用顶部选择框回到以前的学习日。词库剩余新词不足时，使用已学词补足每天 100 词和 50 组，并标为复习。');p.write_text(s,encoding='utf8')
d=json.loads((b/'sources/dataset.json').read_text(encoding='utf8'));coverage=json.loads((b/'sources/coverage.json').read_text(encoding='utf8'))
report=f'''# 词库合并报告

生成日期：2026-10-06

## 导入范围

- 全能词：PDF 第 6–162 页，2848 条原始记录，合并重复英文后 2846 个词。按左侧单词列独立复查，未遗漏任何单词（missing = {len(coverage['missing'])}）。
- 精准释义：扫描 PDF 第 2–3 页，62 行解释，重复单词的多个解释均保留。
- 熟词僻义：扫描 PDF 第 2–5 页，146 行有释义记录。表格中为空的释义格未凭空添加；重复记录合并保留。
- 全能词合并后共 {len(d['words'])} 个词条，精准释义优先，熟词僻义补充。主书不存在的补充词条排在最后。
- 青山等价词：全部 13 页，508 条有效词对。人工核查并补回 8 条跨列或倒置识别失败记录。
- 真经等价词：32 页中包含词表的页面，拆出 1258 条二元词对，包括多搭档记录。
- 等价词合并后共 {len(d['pairs'])} 对；消除 {d['meta']['duplicatesMerged']} 条重复记录，释义与来源不丢弃。

## 合并规则

同一英文的精准释义、熟词僻义、词典/常见义分别保留，练习优先使用精准释义，其次重要僻义，其次主书解释。

等价词按无序英文词对去重。A-B 与 B-A 合并，A-B 与 A-C 独立保留，避免传递合并扩大适用语境。源表一个词有多个搭档时拆成独立词对。多义词对练习使用对应义项，并保留原表全部解释可查阅。

原书列出的词对不保证在所有语境下可互换。六选二是中文词义提示下的词对识别训练，没有编造真题句子。

## 核对与规范化

扫描文字共检查 21 条低置信度/空释义记录。空释义格如 block、meet 属原表空格，不补造新释义。修复 rare 第 5 页短表识别遗漏的 6 行。全部单词与词对都保留 PDF 页码和原件链接。

显然的拼写笔误统一为标准拼写，以便跨书合并：{', '.join(a+' → '+v for a,v in d['meta']['normalizedSpellings'].items())}。这些对应的原件仍可核对。

真经表中连写短语加回空格，例如 insulatedfrom → insulated from、ruleout → rule out、ringtrue → ring true。完整规范化映射见 dataset.json 的 meta。

核对修复：opprobrium/vituperation 的中文为“谩骂”，reverence/veneration 为“尊重”；恢复 doubt/reservation、splendor/sumptuousness 等倒置识别失败记录。未对整本资料逐字人工校订，原资料本身的词义或词对适用范围仍需在实际题目中判断。

## 每日计划

共 30 个学习日，每天全能词 100 个、等价词 50 组。按资料顺序分配新词，词库新词不足后以已学词补足并标记为复习；当天词条不重复。

全能词翻卡 4×25，中文选择检测覆盖每个词，连连看 30+30+30+10。

等价词翻卡 5×10，双向搭档覆盖每对的两个方向，六选二覆盖当天每对。错题返回未通过队列；错词连续答对两次移出错词本。

## 可复核文件

sources/dataset.json 保存最终完整词库；各 *-rows.json 保留识别后的三列逐行记录；各 *-ocr.json 保留识别坐标和置信度；coverage.json 记录全能词独立覆盖检查；tools 中保留整理与校验代码。
'''
(b/'sources/词库合并报告.md').write_text(report,encoding='utf8')
print('Finalized',len(d['words']),len(d['pairs']))
