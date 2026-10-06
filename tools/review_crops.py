from pathlib import Path
import json
from PIL import Image
b=Path('F:/GRE背单词网站/sources')
jobs=[('pairs',1,'accession'),('pairs',5,'immaterial'),('pairs',5,'impair'),('pairs',7,'meticulousness'),('pairs',8,'omnivorous'),('pairs',10,'predilection'),('pairs',11,'splendor'),('pairs',13,'reservation'),('pairs',11,'reverence'),('pairs',8,'opprobrium')]
for tag,pi,word in jobs:
 data=json.loads((b/f'{tag}-{pi}-ocr.json').read_text(encoding='utf8'))
 hits=[r for r in data if word in r[1]]
 if not hits:continue
 y=min(q[1] for q in hits[0][0]);im=Image.open(b/f'{tag}-{pi}.png');im.crop((190,max(0,y-40),1300,y+110)).save(b/f'review-{word}.png')
