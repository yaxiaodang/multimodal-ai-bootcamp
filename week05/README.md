# Week 05｜Document AI 任务地图

当前阶段：三份自制中文单页文档与预览已准备；本人已确认数字 PDF 的标题层级、主要内容顺序和双栏阅读方式。下一步确认该页是否有表格及公式内容，再补齐其余结构与另外两份文档的人工预期；工具实验尚未开始。

Git 保存：分支 `codex/week05-document-ai`，准备提交 `dd0522d`；GitHub 同步因当前环境缺少可用认证而未成功，当前成果仅本地保存。

课程入口：[第五周要求](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-5document-ai)。
本周目标：理解不同文档任务的边界，依据三类文档的实际结果选择一个研究问题。材料将在第六周继续用于 Docling Pipeline。

## 整体流程与分工

| 步骤 | 本人完成的学习活动 | Codex 完成的基础工作 | 留下的证据 |
| --- | --- | --- | --- |
| 1. 认识任务 | 用自己的话区分五种任务及公式识别 | 提供解释、讨论例子 | docs/task-map.md |
| 2. 选择文档 | 选择数字 PDF、扫描件、复杂表格文档各一份 | 归档、记录来源与版本、计算哈希 | samples/README.md、configs/document-manifest.json |
| 3. 写人工预期 | 看原页，标注标题、段落、表格、公式、阅读顺序 | 整理记录；在运行前保存版本 | docs/manual-expectations.md |
| 4. 运行和对照 | 运行命令，检查工具输出，解释与预期的差异 | 准备命令或脚本、配置、日志位置 | runs/、reports/comparison.md |
| 5. 分析与选题 | 归纳至少三类实际错误，选择一个探索方向 | 整理证据与学习记录 | reports/error-analysis.md、docs/research-direction.md、../learning-log.md |

人工预期须先于工具输出形成。后续若发现标注错误，应记录修订理由并保留原版本；不能照着工具答案倒写预期。

## 目录与用途

| 位置 | 用途 |
| --- | --- |
| samples/ | 三份自制 PDF、页面 PNG 预览、制作来源与字体许可 |
| configs/document-manifest.json | 输入路径、制作方法、版本、页码、文件与预览哈希、依赖与字体信息 |
| docs/task-map.md | 根据对话整理的任务地图概念草稿，实际工具与判定规则待本人确认 |
| docs/manual-expectations.md | 人工预期结构，独立于工具输出 |
| docs/research-direction.md | 待本人选择的探索方向、研究问题和成功标准 |
| runs/ | 未来运行的原始输出、日志与配置，当前只有说明 |
| reports/ | 对照、真实错误分析模板 |
| evidence/environment.txt | 本次实际检查到的环境信息 |
| evidence/material-preparation.txt | 输入制作检查与同环境重复生成的原始记录，非工具实验输出 |
| scripts/prepare_documents.py | 生成三份教学文档与预览，不运行 OCR / 文本提取，不填写人工预期 |
| requirements.txt | 材料生成依赖，与根目录基础依赖分开保存 |

## 环境与建议的初始工具

已检查 Ubuntu 22.04.5 LTS；项目 `.venv` 为 Python 3.10.12；PDF 工具为 Poppler 22.02.0。系统默认 `python3` 为 3.14.7，与项目解释器不同。材料制作阶段新增安装 ReportLab 4.4.10，沿用 Pillow 11.3.0 与 charset-normalizer 3.5.1；依赖检查通过，未安装 OCR / Docling，未下载模型。

中文和数字分别使用已有的 DroidSansFallbackFull.ttf 与 DejaVuSans.ttf。生成程序嵌入字体子集，扫描 PDF 则只保存整页图像。系统准备依赖是 poppler-utils、fonts-droid-fallback、fonts-dejavu-core，本机均已具备。

建议先使用 `pdftotext` 建立 CPU 文本提取基线，再用实际缺失的结构提出问题。它读取 PDF 已有文字内容，不执行扫描图像 OCR；纯文本也不显式表示标题层级、单元格合并等结构。扫描 PDF 可能已有 OCR 文字层，不能仅凭文件扩展名或能否选中文字判定来源。最终工具和参数在材料确定后记录。

参考：[Ubuntu pdftotext 手册](https://manpages.ubuntu.com/manpages/jammy/man1/pdftotext.1.html)。课程列出的进一步工具入口：[PaddleOCR](https://www.paddleocr.ai/main/en/index.html)、[Hugging Face 文档问答](https://huggingface.co/docs/transformers/tasks/document_question_answering)。

## 当前唯一开始入口

概念辨析记录见 [任务地图](docs/task-map.md)。第一份文档的标题和主要区域阅读顺序已记录在 [人工预期](docs/manual-expectations.md)。继续查看 [原页预览](samples/previews/digital_pdf.png)，判断是否包含表格，并写出公式、说明上下标关系。后续再补齐其余元素、检查规则和另外两份文档的标注。

如需在 VS Code 中切换到本仓库，在 **Remote SSH 连接 Ubuntu 后的终端**运行：

```bash
cd /home/yaxiaodang/multimodal-ai-bootcamp
```

作用：把终端工作目录切换到仓库根目录，后续相对路径都从这里开始。文件可通过 VS Code 左侧资源管理器打开。Python 程序出现时，再使用下列命令：

```bash
source .venv/bin/activate
```

作用：让当前终端的 `python` 和 `pip` 使用已有项目虚拟环境。它不安装依赖，也不影响系统 PDF 命令。

实际实验命令、参数作用与输出位置将在材料和人工预期确定后补充；本阶段没有完整实验运行入口。

## 材料生成程序的作用与复现

程序依次绘制数字页、制作模拟扫描页、绘制复杂表格页，渲染最终 PDF 预览并写入输入清单。它只准备输入，不提取正文，不生成参考标注或评价。制作检查见 [记录](evidence/material-preparation.txt)，教学内容与许可见 [来源说明](samples/README.md)。

以下是制作复现说明，本轮已由 Codex 完成，不是当前需要本人执行的学习任务。所有命令从仓库根目录执行，并使用已激活的 `.venv`。

```bash
python -m pip install -r week05/requirements.txt
```

作用：安装固定的材料生成依赖。本机已完成；新机器还需准备上述系统工具和字体。

```bash
python week05/scripts/prepare_documents.py --help
```

作用：查看材料生成程序的用途和输出目录参数，不修改任何材料。

```bash
python week05/scripts/prepare_documents.py --output-dir /tmp/week05-materials-rebuild
```

作用：在指定目录重新生成 PDF、预览与清单；目录已有生成材料时会拒绝覆盖。该操作不修改本仓库中的人工预期。默认不传参数时输出到 week05，但已有输入受到覆盖保护。

固定页面内容与坐标，无随机采样，PDF 内部元数据使用 invariant 设置，因此 pdfinfo 中的内部创建时间固定为 2000 年；实际材料制作日期以清单 created_on（2026-10-24）与制作记录为准。本次只验证相同环境的重复生成，其他库或字体版本可能产生不同字节，应依据清单固定版本。

生成库参考：[ReportLab 4.4.10](https://pypi.org/project/reportlab/4.4.10/)、[ReportLab 字体文档](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/)。

## 完成标准

- [x] 三份文档的来源、许可、页码、版本、文件哈希已登记；本人观察待完成。
- [ ] 在运行前写出并保存人工预期；某类元素不存在时明确写“无”。
- [ ] 完成任务地图，知道当前工具主要覆盖哪类任务。
- [ ] 本人执行工具，保留未修改的输出、配置、终端日志和退出状态。
- [ ] 逐项对照预期；记录至少三类有原始证据支持的错误。
- [ ] 选择一个探索方向，提出可验证的研究问题。
- [ ] 更新根目录 learning-log.md，完成 AI 使用披露与人工核验。
- [ ] 将本周阶段成果同步 GitHub，最终状态以提交记录为准。

若当前材料未观察到三类错误，先如实记录，再增加有针对性的合法样本或页码；不得把预想风险写成已经发生的错误。三份教学文档不构成通用 Benchmark。
