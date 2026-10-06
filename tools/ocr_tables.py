from pathlib import Path
import subprocess,json,cv2,numpy as np
from rapidocr_onnxruntime import RapidOCR
base=Path('F:/GRE背单词网站')
engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=4)
jobs=[('precise','青山学堂GRE词表-精准释义V1.0',range(2,4)),('rare','青山学堂GRE词表-熟词僻义V1.0',range(2,6)),('pairs','青山学堂GRE词表-等价词对V2.0',range(1,14))]
for tag,name,pages in jobs:
 allrows=[]
 for page in pages:
    stem=base/'sources'/f'{tag}-{page}'
    subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-r','180','-png',str(Path('F:/GRE')/(name+'.pdf')),str(stem)],check=True,capture_output=True)
    img=cv2.imdecode(np.fromfile(str(stem)+'.png',dtype=np.uint8),cv2.IMREAD_COLOR);gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    bw=cv2.threshold(gray,160,255,cv2.THRESH_BINARY_INV)[1]
    hmask=cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(img.shape[1]//4,1)))
    vmask=cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,img.shape[0]//5)))
    def groups(vals):
        out=[]
        for v in vals:
            if not out or v-out[-1][-1]>3:out.append([v])
            else:out[-1].append(v)
        return [int(np.mean(g)) for g in out]
    ys=groups(np.where(hmask.sum(axis=1)>255*img.shape[1]*.4)[0])
    xs=groups(np.where(vmask.sum(axis=0)>255*img.shape[0]*.3)[0])
    if len(xs)!=4 or len(ys)<3:
        print('BAD GRID',tag,page,xs,ys,flush=True);continue
    clean=img.copy();clean[cv2.dilate(hmask|vmask,np.ones((2,2),np.uint8))>0]=255
    res,_=engine(clean)
    (base/'sources'/f'{tag}-{page}-ocr.json').write_text(json.dumps(res,ensure_ascii=False),encoding='utf-8')
    for lo,hi in zip(ys,ys[1:]):
        cols=[];conf=[]
        for left,right in zip(xs,xs[1:]):
            cells=[r for r in (res or []) if left<np.mean([q[0] for q in r[0]])<right and lo<np.mean([q[1] for q in r[0]])<hi]
            cells.sort(key=lambda r:(round(min(q[1] for q in r[0])/8),min(q[0] for q in r[0])))
            cols.append(' '.join(r[1] for r in cells));conf.extend(r[2] for r in cells)
        allrows.append({'cols':cols,'page':page,'confidence':round(min(conf),3) if conf else 0})
    print(tag,page,'rows',len(ys)-1,'grid',xs,flush=True)
    (base/'sources'/f'{tag}-rows.json').write_text(json.dumps(allrows,ensure_ascii=False,indent=2),encoding='utf-8')
