# Week 07｜Dataset、Benchmark 与负责任使用

本周要回答：**怎样固定一个不会被调参过程污染的测试集，并据此判断文档解析效果？**

课程依据：[第7周路线](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-7datasetbenchmark)、[学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)。

## 先理解主线

上周三份PDF用于观察和开发，本周重新制作24页测试文档与3页开发文档，先保存原页、参考答案、划分和评价规则，再冻结哈希；原样调用上周Docling Pipeline，保存每页未经修改的Markdown/JSON；最后计算总体和切片指标，检查最差五例及数据泄漏。后续方法先用开发集选择，再用同一冻结测试集公平比较。

```text
24份测试PDF + 3份dev PDF + 生成规格参考
             ↓ 先冻结 SHA-256 与指标
24份test → Week06既有 CPU Pipeline → 原始 Markdown/JSON/日志
             ↓ 只读评测
总体 + 类型/布局/扫描档位切片 + 最差五例
             ↓ 本人最后对照原页
解释自动指标遗漏的问题 → 保留v1 → 后续只在dev改进
```

数据集是有来源和参考答案的一组输入；Benchmark还要固定评价协议、baseline和报告方式。测试集参与选择参数后，就不能继续当作独立的最终评价依据。本轮自制模板共享、真实覆盖有限，不等同于正式公共Benchmark。

## 文件与代码各负责什么

| 入口 | 作用 |
| --- | --- |
| [Dataset Card](dataset-card.md) | 来源、split、许可、隐私、偏差、使用边界 |
| [test manifest](data/test-manifest.json)、[dev manifest](data/dev-manifest.json) | 固定样例、类型、路径、输入与参考哈希 |
| [freeze](data/freeze.json) | 固定生成/评价代码、配置、输入和参考的哈希 |
| [指标协议](configs/evaluation.json) | 运行前定义的主指标、辅助指标、失败计分与排序 |
| [baseline配置](configs/baseline.json) | 沿用Week06 CPU/OCR/accurate表格参数，只改变输入/输出目录及参考文件 |
| [生成器](scripts/prepare_dataset.py) | 调用绘图函数制作新文档和参考；冻结后拒绝覆盖 |
| [解析程序](../week06/scripts/run_pipeline.py) | 直接复用既有Pipeline，不复制或调整模型实现 |
| [评测程序](scripts/evaluate.py) | 校验冻结及运行证据，按JSON正文顺序计算内容/结构指标，不读dev调参 |
| [指标测试](scripts/test_evaluation.py) | 手算编辑距离、顺序、表格合并与哈希篡改检测 |
| [实验报告](reports/benchmark-report.md) | 真实总体、切片结果、最差五例与限制 |
| [本人收尾清单](reports/manual-review.md) | 最后集中完成原页核验、学习复盘和实际时长 |

## Ubuntu / VS Code Remote SSH 命令

完整复现实验只需在仓库根目录执行：

```bash
.venv-week06/bin/python week07/scripts/run_benchmark.py
```

作用：先校验冻结文件，再顺序运行24页既有Pipeline，最后自动评价本次新目录，输出 `evaluation.json`；不会覆盖首次报告或本人人工核验清单。已有首次真实结果，无需为了学习阅读而重跑。下列分步命令用于理解各阶段或排错。

以下均在 **VS Code连接到Ubuntu虚拟机后的远程终端** 执行。推理使用已安装的 `.venv-week06`，生成资料使用已有 `.venv`；无需重复安装GPU环境、重新下载模型或付费API。首次运行已由Codex代执行，复习以读取报告为主。

```bash
cd ~/multimodal-ai-bootcamp
```

作用：进入仓库根目录，让配置中的相对路径指向同一套文件。

```bash
.venv-week06/bin/python week07/scripts/evaluate.py --verify-only
```

作用：检查冻结文件哈希，核对24个test/3个dev的ID及精确重复；不推理、不修改数据。通过不代表无模板泄漏。

```bash
.venv-week06/bin/python week06/scripts/run_pipeline.py --config week07/configs/baseline.json --prepare-only
```

作用：校验输入PDF、依赖版本和解析选项；不加载模型、不创建新实验。

```bash
.venv-week06/bin/python week06/scripts/run_pipeline.py --config week07/configs/baseline.json
```

作用：真正运行24页CPU解析，创建独立的 `week07/runs/baseline-时间-标识/`，保存原始输出、日志、版本、快照与耗时。每页重新启动子进程，耗时包含模型加载；失败继续并以非零码结束。运行会消耗数分钟至更久，不需为阅读报告重复执行。继承的 `review.csv` 是第6周核验机制，因ID不重合只含表头；本周本人核验使用收尾清单。

```bash
.venv-week06/bin/python week07/scripts/evaluate.py --run week07/runs/运行目录名称
```

作用：将占位目录名替换成实际baseline目录，读取全部24个样例的原始输出，验证运行配置/输入/输出哈希并生成该目录的 `evaluation.json`；失败样例计0分。不会把缺失页排除出平均值。实际目录见实验报告。

```bash
.venv-week06/bin/python week07/scripts/test_evaluation.py
```

作用：运行四项轻量评价器验证，不调用Docling模型。测试通过说明这些计分逻辑符合手算，不代替对全部样例的视觉判断。

数据已生成并冻结，**不要重建 v1**。生成命令只用于理解其来源：`.venv/bin/python week07/scripts/prepare_dataset.py`；作用是首次制作PDF/参考/manifest和冻结文件，已有freeze时会明确拒绝覆盖。

全新Ubuntu环境的Docling安装、CPU依赖、模型来源见 [Week06环境说明](../week06/docs/environment.md) 和 [锁定依赖](../week06/requirements-lock.txt)；数据PDF和参考已随仓库保存，复现推理不要求安装ReportLab或系统字体。

## 指标怎么读

主指标为逐页规范化字符编辑相似度的宏平均：`1 - 编辑距离 / max(参考长度,预测长度,1)`，越高越好。JSON正文树中的文本和按行列排序、去重复起点的表格文字，与预先写定的参考顺序对照；NFKC、大小写统一、去空格标点，仍保留文字先后。因此文字错误、漏字、多字与部分顺序错误都会降分，标点或标题层级错误可能不降分。

辅助指标包括转换成功率、三个指定标题的两两先后关系、完整表格网格和合并范围精确匹配，以及各页耗时。表格指标检查5×6和5个合并范围；不因数字凑齐就认定结构正确。总体按页面等权；类型各8页。非适用的辅助项记null，转换失败的适用项记0。

本周只运行一个baseline，自主探索选择“数据分布与切片”：观察单/双栏与扫描档位分布及表现，不开展test调参，不把多因素扫描档位比较当成因果消融。

AI完成代码、运行、指标和报告；本人的阅读、视觉核验、学习时长和自评仍需本人最后提供。详见 [收尾清单](reports/manual-review.md)。
