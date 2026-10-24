"""生成三份中文教学 PDF、页面预览与输入清单，不执行 OCR 或文本提取。"""

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import subprocess
import sys
import tempfile
from itertools import groupby
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = Path('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')
FONT_NAME = 'TeachingCJK'
LATIN_PATH = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
LATIN_NAME = 'TeachingLatin'
WIDTH, HEIGHT = A4
DPI = 150
VERSION = '1.0'
CREATED_ON = '2026-10-24'
INK = colors.HexColor('#243447')
BLUE = colors.HexColor('#245b78')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_pdf(path, title):
    # invariant 固定 PDF 内部时间等元数据，便于检查同环境重复生成。
    pdf = canvas.Canvas(str(path), pagesize=A4, invariant=1,
                        pageCompression=1, initialFontName=FONT_NAME)
    pdf.setTitle(title)
    pdf.setAuthor('multimodal-ai-bootcamp / AI-assisted teaching materials')
    pdf.setSubject('Fictional teaching material; not a real business document')
    return pdf


def font_for(char):
    # Droid 是中文备用字体，ASCII 数字/字母改用 DejaVu，避免空白字形。
    return LATIN_NAME if ord(char) < 256 or char == '—' else FONT_NAME


def string_width(value, size):
    return sum(pdfmetrics.stringWidth(char, font_for(char), size) for char in value)


def text(pdf, x, top, value, size=11, color=INK):
    pdf.setFillColor(color)
    for font_name, chars in groupby(value, key=font_for):
        run = ''.join(chars)
        pdf.setFont(font_name, size)
        pdf.drawString(x, HEIGHT - top, run)
        x += pdfmetrics.stringWidth(run, font_name, size)


def paragraph(pdf, x, top, value, width, size=11, leading=20):
    line = ''
    for char in value:
        if string_width(line + char, size) > width:
            text(pdf, x, top, line, size)
            top += leading
            line = char
        else:
            line += char
    if line:
        text(pdf, x, top, line, size)
    return top + leading


def page_header(pdf, title, subtitle):
    text(pdf, 48, 52, title, 21, BLUE)
    text(pdf, 48, 77, subtitle, 10)
    pdf.setStrokeColor(colors.HexColor('#a9bdc8'))
    pdf.setLineWidth(0.8)
    pdf.line(48, HEIGHT - 94, WIDTH - 48, HEIGHT - 94)


def page_footer(pdf, sample_id):
    text(pdf, 48, HEIGHT - 38, '自制教学材料 · 内容与数据均为虚构 · 版本 1.0', 9)
    text(pdf, WIDTH - 180, HEIGHT - 38, f'{sample_id}  /  1', 8)


def digital_document(path):
    pdf = new_pdf(path, '文档处理实验说明')
    page_header(pdf, '第一章 实验方法', '文档处理实验说明 / 教学版本 1.0')
    paragraph(pdf, 48, 127,
              '本实验观察文档内容与结构在转换过程中如何保留。页面采用双栏组织，'
              '请结合段落语义理解各区域之间的联系。', WIDTH - 96)

    left, right, column_width = 48, 320, 225
    text(pdf, left, 204, '1.1 材料与输入', 15, BLUE)
    paragraph(pdf, left, 236,
              '教学小组准备三类材料：数字文档、模拟扫描件与复杂表格文档。'
              '所有数据均为自制，不包含真实个人信息。', column_width)
    paragraph(pdf, left, 340,
              '每份材料先观察一页。检查时记录标题、段落、表格与公式；'
              '页面没有某类元素时，也应明确说明。', column_width)

    text(pdf, right, 204, '1.2 处理与核对', 15, BLUE)
    paragraph(pdf, right, 236,
              '先根据原始页面记录预期，再运行公开工具。'
              '工具结果保留原样，人工评价另行保存。', column_width)
    paragraph(pdf, right, 340,
              '比较时分别检查文字内容、区域关系与阅读顺序。'
              '程序正常结束，并不表示所有结构都已保留。', column_width)

    text(pdf, 48, 474, '1.3 数值示例', 15, BLUE)
    paragraph(pdf, 48, 507,
              '下式仅用于观察上下标的位置关系，其中两个带下标的变量分别表示两个输入数值。',
              WIDTH - 96)
    # 用真实文本对象绘制上下标，保留其视觉结构。
    formula = pdf.beginText(190, HEIGHT - 575)
    formula.setFont('Helvetica', 21)
    formula.textOut('E = x')
    formula.setFont('Helvetica', 12)
    formula.setRise(-6)
    formula.textOut('1')
    formula.setRise(10)
    formula.textOut('2')
    formula.setRise(0)
    formula.setFont('Helvetica', 21)
    formula.textOut(' + x')
    formula.setFont('Helvetica', 12)
    formula.setRise(-6)
    formula.textOut('2')
    formula.setRise(10)
    formula.textOut('2')
    formula.setRise(0)
    pdf.drawText(formula)
    paragraph(pdf, 48, 633,
              '记录说明：不要仅凭文字是否出现判断完整性，还应核对文字在原页中的角色与关系。',
              WIDTH - 96)
    page_footer(pdf, 'digital_pdf')
    pdf.showPage()
    pdf.save()


def table_at(pdf, data, widths, heights, top, spans=()):
    table = Table(data, colWidths=widths, rowHeights=heights)
    style = [
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), INK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor('#8a9aa6')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5eef4')),
    ]
    style.extend(('SPAN', start, end) for start, end in spans)
    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            if value and all(font_for(char) == LATIN_NAME for char in value):
                style.append(('FONTNAME', (col_index, row_index),
                              (col_index, row_index), LATIN_NAME))
    table.setStyle(TableStyle(style))
    width, height = table.wrap(WIDTH - 96, HEIGHT)
    table.drawOn(pdf, (WIDTH - width) / 2, HEIGHT - top - height)


def scanned_source(path):
    pdf = new_pdf(path, '设备借用记录（模拟扫描源页）')
    page_header(pdf, '设备借用记录', '模拟扫描教学页 / 非真实业务记录')
    text(pdf, 48, 133, '记录编号：LAB-DEMO-005', 12)
    text(pdf, 325, 133, '登记日期：2026-10-24', 12)
    text(pdf, 48, 170, '借用单位：教学小组 A', 12)
    text(pdf, 325, 170, '用途：文档数字化练习', 12)
    table_at(pdf, [
        ['设备', '数量', '借出状态', '归还要求'],
        ['扫描仪', '1', '可正常使用', '清洁玻璃面板'],
        ['台灯', '2', '可正常使用', '整理电源线'],
        ['文件夹', '3', '外观完好', '检查夹内无文件'],
    ], [115, 60, 140, 184], [42] * 4, 215)
    text(pdf, 48, 437, '注意事项', 15, BLUE)
    paragraph(pdf, 48, 472,
              '借用前检查设备状态，使用后按表格中的要求整理。'
              '如发现异常，应先记录问题，再暂停使用相关设备。', WIDTH - 96)
    text(pdf, 48, 568, '登记方式：系统演示，无需真实签名。', 12)
    text(pdf, 48, 620, '本页为人工生成后栅格化的模拟扫描件，不代表真实扫描质量。', 10)
    page_footer(pdf, 'scanned_pdf')
    pdf.showPage()
    pdf.save()


def render(pdf_path, prefix):
    subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-singlefile',
                    '-r', str(DPI), '-png', str(pdf_path), str(prefix)], check=True)
    return prefix.with_suffix('.png')


def scan_document(path, workdir):
    source = workdir / 'scan-source.pdf'
    scanned_source(source)
    rendered = render(source, workdir / 'scan-source')
    with Image.open(rendered) as image:
        gray = ImageOps.grayscale(image)
        gray = gray.point(lambda value: round(18 + value * 0.92))
        scanned = gray.rotate(0.6, resample=Image.Resampling.BICUBIC,
                              expand=False, fillcolor=253)
    pdf = new_pdf(path, '设备借用记录（模拟扫描件）')
    # 最终 PDF 只绘制一张页面图像，不绘制任何文字对象或 OCR 层。
    pdf.drawImage(ImageReader(scanned), 0, 0, width=WIDTH, height=HEIGHT)
    pdf.showPage()
    pdf.save()


def complex_table_document(path):
    pdf = new_pdf(path, '教学项目季度费用表')
    page_header(pdf, '教学项目季度费用表', '内部演示数据 / 2026 年第一、第二季度')
    paragraph(pdf, 48, 129,
              '本表记录虚构教学项目的材料与服务费用。金额单位为元；'
              '数量按各项目的计量单位记录，不跨项目求和。', WIDTH - 96)
    table_at(pdf, [
        ['类别', '项目', '第一季度', '', '第二季度', ''],
        ['', '', '数量', '金额（元）', '数量', '金额（元）'],
        ['材料', '纸张（包）', '10', '50', '12', '60'],
        ['', '墨盒（个）', '2', '160', '1', '80'],
        ['服务', '扫描（页）', '20', '40', '0', '0'],
        ['', '装订（本）', '3', '30', '4', '40'],
        ['金额合计', '', '—', '280', '—', '180'],
    ], [65, 122, 72, 84, 72, 84], [34, 34, 50, 50, 50, 50, 45], 208,
        spans=[((0, 0), (0, 1)), ((1, 0), (1, 1)),
               ((2, 0), (3, 0)), ((4, 0), (5, 0)),
               ((0, 2), (0, 3)), ((0, 4), (0, 5)), ((0, 6), (1, 6))])
    text(pdf, 48, 583, '填表说明', 15, BLUE)
    paragraph(pdf, 48, 619,
              '数字 0 表示该季度实际为零；长横线表示该位置不适用。'
              '金额合计只对同一季度的金额列求和。', WIDTH - 96)
    paragraph(pdf, 48, 699,
              '复核备注：本表仅供文档结构学习，不对应真实采购、报销或财务记录。', WIDTH - 96, size=10)
    page_footer(pdf, 'complex_table')
    pdf.showPage()
    pdf.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT,
                        help='生成目录，默认 week05；已有材料时拒绝覆盖，可指定新的临时目录')
    args = parser.parse_args()
    if (not FONT_PATH.is_file() or not LATIN_PATH.is_file()
            or shutil.which('pdftoppm') is None):
        parser.error('需要 fonts-droid-fallback / fonts-dejavu-core 字体及 poppler-utils。')
    output = args.output_dir.resolve()
    samples, configs = output / 'samples', output / 'configs'
    ids = ['digital_pdf', 'scanned_pdf', 'complex_table']
    targets = [samples / f'{sample_id}.pdf' for sample_id in ids]
    targets += [samples / 'previews' / f'{sample_id}.png' for sample_id in ids]
    targets += [configs / 'document-manifest.json']
    # 初始空白清单可替换；一旦输入已有哈希或文件，拒绝覆盖。
    existing = [path for path in targets if path.exists()]
    initial_manifest = configs / 'document-manifest.json'
    if existing == [initial_manifest]:
        current = json.loads(initial_manifest.read_text(encoding='utf-8'))
        if (current.get('status') == 'awaiting_user_selection'
                and all(item.get('sha256') is None for item in current.get('documents', []))):
            existing = []
    if existing:
        parser.error('目标已有材料或清单；请使用 --output-dir 指定新的目录，避免覆盖已标注文档。')
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    pdfmetrics.registerFont(TTFont(LATIN_NAME, str(LATIN_PATH)))
    (samples / 'previews').mkdir(parents=True, exist_ok=True)
    configs.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='week05-make-') as work:
        digital_document(samples / 'digital_pdf.pdf')
        scan_document(samples / 'scanned_pdf.pdf', Path(work))
        complex_table_document(samples / 'complex_table.pdf')
    documents = []
    methods = [
        'ReportLab text objects and vector drawing; embedded Chinese font; no OCR',
        'Synthetic source rasterized at 150 DPI; grayscale, contrast adjustment, 0.6 degree rotation; image-only PDF; no OCR',
        'ReportLab vector table with merged cells and text objects; embedded Chinese font; no OCR',
    ]
    for sample_id, category, method in zip(ids, ['digital_pdf', 'scanned_document', 'complex_table_document'], methods):
        path = samples / f'{sample_id}.pdf'
        preview = render(path, samples / 'previews' / sample_id)
        documents.append({
            'id': sample_id, 'category': category,
            'path': path.relative_to(output).as_posix(),
            'preview': preview.relative_to(output).as_posix(),
            'source': 'Self-generated, AI-assisted fictional teaching material; user selected route A',
            'created_on': CREATED_ON, 'accessed_on': None,
            'license_or_permission': 'CC0-1.0 for generated teaching content; embedded fonts retain their licenses (Droid Apache-2.0, DejaVu font license; see samples/licenses)',
            'redistribution_allowed': True,
            'privacy_review': 'Synthetic content only; no real personal or business records',
            'version': VERSION, 'pages': [1], 'page_count': 1,
            'sha256': digest(path), 'preview_sha256': digest(preview),
            'generation_method': method,
            'role': 'teaching_probe; not a benchmark or model evaluation result',
        })
        print(f'Prepared {path.relative_to(output)} ({path.stat().st_size} bytes)')
    manifest = {
        'schema_version': 1, 'status': 'prepared_awaiting_user_observation',
        'page_numbering': 'PDF physical pages, 1-based',
        'version': VERSION,
        'generation': {
            'script': 'scripts/prepare_documents.py', 'python': sys.version.split()[0],
            'packages': {name: importlib.metadata.version(name)
                         for name in ['reportlab', 'Pillow', 'charset-normalizer']},
            'pdftoppm': subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True, check=True).stderr.splitlines()[0],
            'fonts': [{'file': font.name, 'sha256': digest(font)}
                      for font in [FONT_PATH, LATIN_PATH]],
            'render_dpi': DPI, 'random_seed': None,
            'randomness': 'No random noise or sampling; fixed geometry and PDF invariant metadata',
        },
        'documents': documents,
    }
    (configs / 'document-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Saved 3 PDFs, 3 rendered previews and input manifest. No OCR/text extraction experiment was run.')


if __name__ == '__main__':
    main()
