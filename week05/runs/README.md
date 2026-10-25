# 原始运行证据

本人首次基线为 [baseline-20261025T105130-507b20](baseline-20261025T105130-507b20/)，2026-10-25 10:51:30（Asia/Shanghai）运行，三份文档均 exit=0。Python 3.10.12、pdftotext 22.02.0；当前 7/11 项已记录：1 项正确、1 项错误、2 项结构未表达、3 项工具不支持，复杂表格 4 项待评价；原始 txt 与快照不变。

入口为仓库根目录执行 `.venv/bin/python week05/scripts/run_baseline.py`，作用是明确使用项目解释器，核对输入后调用 pdftotext，依次保存三份 PDF 的纯文本结果与运行证据，评价由本人完成。

后续每次运行使用独立目录，保存：工具和版本、完整命令及参数、输入路径与 SHA-256、页码、开始时间、耗时、退出状态、标准输出/错误日志，以及未经人工修改的工具结果。

每轮自动创建 baseline-日期时间-标识/，其中：

| 文件 | 内容 |
| --- | --- |
| digital_pdf.txt / scanned_pdf.txt / complex_table.txt | 工具未经改写的原始结果；空白也保留 |
| 对应 .stdout.log / .stderr.log | 原始标准输出与错误日志 |
| run-metadata.json | 配置、版本、时间、输入/输出哈希、命令、退出状态、耗时及代码版本 |
| tool-version.txt | 工具报告的完整版本信息 |
| snapshots/ | 本轮的配置、输入清单、人工预期、检查计划与程序源码副本 |
| review.csv | 11 项检查与预期；judgment、evidence_location、reason 留空，待人工评价 |

人工预期原文件位于 ../docs/manual-expectations.md；本轮应依据 snapshots 中保存的版本评价，不用后来修改的预期替换历史。评价由 Codex 根据本人判断整理到 ../reports/ 或本轮 review.csv，不能修改原始 txt 制造正确结果。失败运行同样保留。
