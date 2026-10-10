"""生成固定的十张教学样例和人工核验清单，不运行模型。"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
items = []
(ROOT / "samples").mkdir(exist_ok=True)
shape = Image.new("RGB", (320, 320), "white")
draw = ImageDraw.Draw(shape)
draw.rectangle((30, 100, 130, 220), fill="red")
draw.ellipse((190, 110, 290, 210), fill="blue")
shape.save(ROOT / "samples" / "shapes.png")


def canvas():
    image = Image.new("RGB", (512, 512), "white")
    return image, ImageDraw.Draw(image)


def text(draw, xy, value, size=28):
    draw.text(xy, value, fill="black", font=ImageFont.truetype(FONT, size))


def add(sample_id, category, image, question, reference, criteria):
    target = ROOT / "samples" / f"{sample_id}.png"
    if image is not None:
        image.save(target)
    items.append({"id": sample_id, "category": category,
                  "image": f"samples/{sample_id}.png", "question": question,
                  "reference_answer": reference, "criteria": criteria,
                  "source": "self-generated with Pillow; no third-party image or private data",
                  "license": "CC0-1.0 (generated image)", "split": "teaching_probe"})


add("shapes", "spatial", None,
    "Describe the two colored shapes and their positions in one short sentence.",
    "A red rectangle is on the left and a blue circle is on the right.",
    "Must name both colors, rectangle/circle, and left/right; square is inaccurate.")

im, d = canvas()
for x, y in [(65, 65), (205, 65), (345, 65), (65, 210), (205, 210), (345, 210), (205, 355)]:
    d.ellipse((x, y, x+65, y+65), fill="green")
add("count", "counting", im, "How many green circles are visible?", "7", "Exactly seven circles.")

im, d = canvas()
d.rectangle((70, 50, 210, 110), fill="red")
d.ellipse((290, 315, 400, 425), fill="blue")
add("position", "spatial", im, "Is the red rectangle above or below the blue circle?", "Above", "Red is above blue.")

im, d = canvas()
text(d, (30, 120), "Invoice ID: AB-7093", 34)
text(d, (30, 220), "Total: USD 128.50", 34)
add("invoice", "ocr", im, "What is the invoice ID? Copy it exactly.", "AB-7093", "Exact ID including hyphen and digits.")

im, d = canvas()
for i in range(12):
    text(d, (25, 25+i*36), f"Record {i+1:02d}: code ZX-{4100+i}", 18)
add("dense_text", "ocr", im, "What code is shown for Record 09? Copy it exactly.", "ZX-4108", "Exact code from row 09.")

im, d = canvas()
for y in [70, 150, 230, 310, 390]:
    d.line((40, y, 470, y), fill="black", width=2)
for x in [40, 260, 470]:
    d.line((x, 70, x, 390), fill="black", width=2)
for y, a, b in [(90, "Item", "Price"), (170, "Pen", "3"), (250, "Book", "12"), (330, "Bag", "25")]:
    text(d, (60, y), a); text(d, (280, y), b)
add("table", "ocr", im, "What is the price of the Book in the table?", "12", "Read Book row, Price column.")

im, d = canvas()
d.line((55, 420, 470, 420), fill="black", width=3)
for x, height, label in [(90, 140, "A"), (220, 280, "B"), (350, 210, "C")]:
    d.rectangle((x, 420-height, x+60, 420), fill="steelblue")
    text(d, (x+15, 445), label)
add("chart", "reasoning", im, "Which labeled bar is tallest?", "B", "Identify bar B, not arbitrary numerical values.")

im, d = canvas()
text(d, (30, 90), "Shopping list", 34)
text(d, (30, 190), "Apples: 3 x USD 2", 30)
text(d, (30, 270), "Bread: 1 x USD 4", 30)
add("arithmetic", "reasoning", im, "What is the total cost in USD?", "10", "3*2+1*4 = 10.")

im, d = canvas()
text(d, (40, 100), "STORE RECEIPT", 34)
text(d, (40, 220), "Item: Notebook", 30)
text(d, (40, 300), "Total: USD 5.00", 30)
add("missing_date", "hallucination", im, "What purchase date is shown on the receipt?", "No purchase date is shown.", "Must say date is absent; invented date fails.")

im, d = canvas()
text(d, (25, 160), "Account code: 583194", 30)
d.rectangle((250, 145, 495, 220), fill="black")
add("occluded", "hallucination", im, "What is the full account code?", "Cannot determine the full code because it is covered.", "Must not invent the covered digits; source text is not visible evidence.")

(ROOT / "configs" / "sample-manifest.json").write_text(json.dumps(items, ensure_ascii=False, indent=2)+"\n")
rows = ["# 固定教学样例清单", "", "生成图片使用 CC0-1.0；字体为系统 DejaVuSans（字体许可独立）。没有私人信息、外部照片或正式 benchmark；结论仅适用于这些教学探针。", "", "| ID | 类型 | 问题 | 参考答案 |", "| --- | --- | --- | --- |"]
rows += [f"| {x['id']} | {x['category']} | {x['question']} | {x['reference_answer']} |" for x in items]
(ROOT / "samples" / "README.md").write_text("\n".join(rows)+"\n")
print(f"Prepared {len(items)} samples; no model inference performed.")
