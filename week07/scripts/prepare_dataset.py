"""制作固定教学数据；一旦 freeze.json 存在即拒绝覆盖。"""
import sys
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageFilter
from reportlab.lib.utils import ImageReader
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'week05/scripts'))
import prepare_documents as draw
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
WEEK = ROOT / 'week07'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def main():
    if (WEEK/'data/freeze.json').exists():
        raise SystemExit('测试集已冻结，拒绝重建。新数据请建立新版本，勿覆盖 v1。')
    pdfmetrics.registerFont(TTFont(draw.FONT_NAME, str(draw.FONT_PATH)))
    pdfmetrics.registerFont(TTFont(draw.LATIN_NAME, str(draw.LATIN_PATH)))
    docs, dev = [], []
    for split, count in [('dev', 1), ('test', 8)]:
        for kind in ['digital', 'scan', 'table']:
            for i in range(count):
                serial = (i+1 if split == 'test' else 91)
                sample_id = f'{split}_{kind}_{serial:02}'
                path = WEEK/f'data/{split}/{sample_id}.pdf'
                n = serial*17 + {'digital':100,'scan':300,'table':500}[kind]
                title = {'digital':'实验流程记录','scan':'设备检查记录','table':'物资统计表'}[kind]
                title += f' {n}'
                blocks = [title]
                order = []
                table = None
                with tempfile.TemporaryDirectory() as temp:
                    source = Path(temp)/'source.pdf'
                    pdf = draw.new_pdf(source, title)
                    draw.text(pdf, 48, 58, title, 21)
                    if kind in ['digital','scan']:
                        # 数字页交替单栏/双栏；扫描页单栏、四档质量。参考顺序按栏优先。
                        headings = ['第一步 材料登记','第二步 处理检查','第三步 结果归档']
                        content = [f'材料编号为 TEST-{n}，本批数量为 {n+3}。',
                                   f'处理温度为 {n%20+20} 度，检查时间为 {n%30+10} 分钟。',
                                   f'归档批次为 GROUP-{n+9}，结果仅用于虚构教学实验。']
                        for j,(heading,body) in enumerate(zip(headings, content)):
                            two = kind=='digital' and serial%2==0
                            x, top = ((48 if j<2 else 320), (155+j*200 if j<2 else 155)) if two else (48,155+j*160)
                            draw.text(pdf,x,top,heading,15)
                            draw.paragraph(pdf,x,top+38,body,220 if two else 490,12)
                            blocks += [heading,body]
                        order = headings
                    else:
                        table = [ ['类别','项目','上期','','本期',''],
                                  ['','','数量','金额','数量','金额'],
                                  ['耗材','纸张',str(n),str(n*5),str(n+2),str((n+2)*5)],
                                  ['','墨盒',str(n+4),str((n+4)*9),str(n+6),str((n+6)*9)],
                                  ['设备','支架',str(n+8),str((n+8)*7),str(n+10),str((n+10)*7)] ]
                        spans = [((0,0),(0,1)),((1,0),(1,1)),((2,0),(3,0)),((4,0),(5,0)),((0,2),(0,3))]
                        draw.table_at(pdf,table,[60,80,80,80,80,80],[38]*5,155,spans)
                        blocks += [v for row in table for v in row if v]
                        note=f'核对批次 BATCH-{n}，单位为件和元。'
                        draw.paragraph(pdf,48,410,note,490,12)
                        blocks.append(note)
                    pdf.showPage(); pdf.save()
                    if kind=='scan':
                        dpi=[150,120,100,80][i%4]
                        subprocess.run(['pdftoppm','-scale-to',str(int(842*dpi/72)),'-singlefile','-png',str(source),str(Path(temp)/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                        with Image.open(Path(temp)/'page.png') as image:
                            image=image.convert('L').filter(ImageFilter.GaussianBlur([0,0.3,0.6,0.9][i%4]))
                            image=image.rotate([0,0.5,1,2][i%4],resample=Image.Resampling.BICUBIC,fillcolor=255)
                            out=draw.new_pdf(path,title)
                            out.drawImage(ImageReader(image),0,0,width=draw.WIDTH,height=draw.HEIGHT)
                            out.showPage(); out.save()
                    else:
                        path.write_bytes(source.read_bytes())
                ref=WEEK/f'references/{sample_id}.json'
                save(ref,{'id':sample_id,'blocks':blocks,'reading_order':order,'table_grid':table,
                          'table_spans':[[0,2,0,1],[0,2,1,2],[0,1,2,4],[0,1,4,6],[2,4,0,1]] if table else [],
                          'annotation_source':'generator specification; human review pending'})
                entry={'id':sample_id,'path':str(path.relative_to(ROOT)),'sha256':sha(path),'pages':[1],'page_count':1,
                       'type':kind,'split':split,'source':'new fictional synthetic teaching document CC0-1.0',
                       'reference':str(ref.relative_to(ROOT)),'reference_sha256':sha(ref),
                       'layout':'two_column' if kind=='digital' and serial%2==0 else 'table' if kind=='table' else 'single_column',
                       'scan_quality':i%4 if kind=='scan' else None}
                (docs if split=='test' else dev).append(entry)
    for name,entries in [('test',docs),('dev',dev)]:
        save(WEEK/f'data/{name}-manifest.json',{'schema_version':1,'version':'1.0','path_base':'repository_root','documents':entries})
    config=json.loads((ROOT/'week06/configs/baseline.json').read_text())
    config.update(name='week07-frozen-docling-baseline-v1',manifest='week07/data/test-manifest.json',output_root='week07/runs',references=['week07/configs/evaluation.json','week07/data/freeze.json'])
    save(WEEK/'configs/baseline.json',config)
    paths=[WEEK/'data/test-manifest.json',WEEK/'data/dev-manifest.json',WEEK/'configs/evaluation.json',WEEK/'configs/baseline.json',Path(__file__),WEEK/'scripts/evaluate.py']
    paths += [ROOT/d[k] for d in docs+dev for k in ['path','reference']]
    save(WEEK/'data/freeze.json',{'frozen_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'version':'1.0','seed':None,'files':{str(p.relative_to(ROOT)):sha(p) for p in paths}})
    print('已冻结 test=24、dev=3，包含输入、参考、指标与 baseline 配置的 SHA-256。')
if __name__=='__main__': main()
