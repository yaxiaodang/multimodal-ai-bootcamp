# 单图样例来源

`shapes.png` 由 `../scripts/prepare_samples.py` 用 Pillow 生成，320×320、RGB、白色背景。
左侧红色矩形，右侧蓝色圆形。没有随机过程、私人信息或第三方素材；非外部数据集，version/split 不适用。未单独声明素材许可证，第三方素材许可不适用。

用于检查颜色、形状和左右位置。参考答案见 `../configs/single-config.json`，参考答案仅供人工核验，不传入模型。

# 固定教学样例清单

生成图片使用 CC0-1.0；字体为系统 DejaVuSans（字体许可独立）。没有私人信息、外部照片或正式 benchmark；结论仅适用于这些教学探针。

| ID | 类型 | 问题 | 参考答案 |
| --- | --- | --- | --- |
| shapes | spatial | Describe the two colored shapes and their positions in one short sentence. | A red rectangle is on the left and a blue circle is on the right. |
| count | counting | How many green circles are visible? | 7 |
| position | spatial | Is the red rectangle above or below the blue circle? | Above |
| invoice | ocr | What is the invoice ID? Copy it exactly. | AB-7093 |
| dense_text | ocr | What code is shown for Record 09? Copy it exactly. | ZX-4108 |
| table | ocr | What is the price of the Book in the table? | 12 |
| chart | reasoning | Which labeled bar is tallest? | B |
| arithmetic | reasoning | What is the total cost in USD? | 10 |
| missing_date | hallucination | What purchase date is shown on the receipt? | No purchase date is shown. |
| occluded | hallucination | What is the full account code? | Cannot determine the full code because it is covered. |
