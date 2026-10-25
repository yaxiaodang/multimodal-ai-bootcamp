# 原始 prediction 索引

本目录对齐专题 Week 5 提交入口。[index.csv](index.csv) 记录两轮共六份原始文本的仓库相对路径、输入/输出哈希、字节数、退出码及评价/元数据路径；CSV 中路径均从仓库根目录解析。

原始文件继续保存在带运行快照的 runs 目录，不移动、不复制改写。实际内容入口：

| 运行 | 数字 PDF | 模拟扫描件 | 复杂表格 |
| --- | --- | --- | --- |
| 默认参数 | [TXT](../runs/baseline-20261025T105130-507b20/digital_pdf.txt) | [TXT](../runs/baseline-20261025T105130-507b20/scanned_pdf.txt) | [TXT](../runs/baseline-20261025T105130-507b20/complex_table.txt) |
| 只加 -layout | [TXT](../runs/baseline-20261025T113919-b11603/digital_pdf.txt) | [TXT](../runs/baseline-20261025T113919-b11603/scanned_pdf.txt) | [TXT](../runs/baseline-20261025T113919-b11603/complex_table.txt) |

扫描文本只有 0x0c，空白本身也作为结果保留。目录说明、日志、命令和参考快照见 [runs/README.md](../runs/README.md)；人工预期见 [manual-expectations.md](../docs/manual-expectations.md)。
