# Week07 Benchmark Report

状态：Codex已实际执行24页baseline和自动评测；本人视觉核验、实际学习时间和自评待补。结果仅适用于本地自制教学测试集v1。

## 协议与baseline

先生成参考、冻结24个test/3个dev输入及指标/配置，再运行Week06原有Docling CPU Pipeline。OCR和accurate表格模式保持不变，无Prompt、训练或test调参；dev尚未使用。基准模型与锁定依赖见第6周证据。

原始运行：[baseline-20261111T144702-4ebb49](../runs/baseline-20261111T144702-4ebb49/)；[指标原始JSON](../runs/baseline-20261111T144702-4ebb49/evaluation.json)；[输入与配置冻结](../data/freeze.json)。运行元数据中的Git提交为本周提交前的基底，实际源码有快照/哈希，最终归档见Git历史。

主指标是逐页规范化字符编辑相似度宏平均，0–1、越高越好；失败页计0并留在分母。辅助项按适用页计算。详细定义先于推理保存在 [evaluation.json](../configs/evaluation.json)，不是官方OmniDocBench评分，也不是生产准确率。

## 总体与切片

| 分组 | 页数 | 字符相似度 | 转换成功率 | 标记对顺序 | 表格精确匹配 | 总秒数 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 总体 | 24 | 0.9676 | 1.0000 | 0.7083 | 0.0000 | 996.38 |
| type=digital | 8 | 1.0000 | 1.0000 | 1.0000 | — | 119.20 |
| type=scan | 8 | 0.9505 | 1.0000 | 0.4167 | — | 680.61 |
| type=table | 8 | 0.9521 | 1.0000 | — | 0.0000 | 196.57 |
| layout=single_column | 12 | 0.9670 | 1.0000 | 0.6111 | — | 744.54 |
| layout=table | 8 | 0.9521 | 1.0000 | — | 0.0000 | 196.57 |
| layout=two_column | 4 | 1.0000 | 1.0000 | 1.0000 | — | 55.28 |
| scan_quality=0 | 2 | 0.9560 | 1.0000 | 0.3333 | — | 207.36 |
| scan_quality=1 | 2 | 0.9451 | 1.0000 | 0.3333 | — | 199.22 |
| scan_quality=2 | 2 | 0.9011 | 1.0000 | 0.0000 | — | 172.89 |
| scan_quality=3 | 2 | 1.0000 | 1.0000 | 1.0000 | — | 101.14 |

耗时为各页墙钟时间相加，包含各自子进程/模型加载与OCR；不等于纯模型速度、总学习时间或跨机器性能比较。扫描4档每档2页，DPI/旋转/模糊共同变化，仅为描述性切片。

## 如何解释这轮结果

24/24页转换成功，主指标为0.9676，但8/8表格都未达到严格结构精确匹配；这不等于整张表的所有数据都错误，而是每页至少一处网格文字位置或合并范围与参考不符。主指标无法代替结构判断。

扫描档位3的两页字符分为1.0，档位2两页反而较低。样例少且同时改变多个因素，不能据此推断更模糊/更低DPI会提高OCR。数字页字符分全部1.0，也不能推出标题层级或标点全部正确。

标记对顺序采用完整标题字符串匹配，缺失标记也判错，所以0.4167同时反映OCR漏字/块内重排和先后关系，不能解释成“58.33%的页面阅读顺序颠倒”。三个标记每页3对，16个适用页面共48对，其中34对满足规则；扫描8页共24对，其中10对满足。表格精确匹配分母8页，转换成功率和主指标分母24页。

## 最差五例的解释与错误分类

以下为Codex根据参考、原始JSON与原页预览作出的定位，本人核验仍待完成：

| 样例 | 观察到的具体差异 | 归类与影响 |
| --- | --- | --- |
| test_scan_03 | 参考“第一步材料登记”预测为“步材料登记第”；“第二步处理检查”预测为“处理检查第二步” | 漏“一”及块内次序重排；标题标记无法完整匹配，不能直接说整页段落全部倒序 |
| test_scan_07 | 同样出现“步材料登记第”和“处理检查第二步”，数值换成419等 | 与03共享模板和档位的同型错误；保留为真实低分样例，但不称为独立新错误机制 |
| test_table_05 | 上期/本期表头在预测网格起点顺序中出现在类别/项目前；原页类别与项目均应跨两行 | 表头定位/合并关系错误；数据数字基本保留不能弥补结构不匹配 |
| test_scan_01 | 标题被输出成“317”再“设备检查记录”；第一步缺“一” | 标题块顺序错误与OCR漏字；编号仍出现，字符存在不等于顺序正确 |
| test_scan_02 | “第一步材料登记”预测为“材料登记第步” | 漏字与块内重排；其他主体内容大体保留，需分项解释 |

另一个主指标盲区：test_scan_08的字符分1.0，但JSON中页面标题与步骤文字均为text，第一步标题还和正文合成一块。原页的字号/段落结构未因此得到正确的标题角色表示。本人最后可用这页说明“文字正确≠结构完整”。

表格辅助核查示例：test_table_01的“项目”实际范围为零基行[1,2)、列[1,2)，参考应为行[0,2)、列[1,2)，因此原页纵向合并未恢复。test_table_05中“类别”和“项目”被放到第二行，问题更明显。所有跨度均按JSON的起点含、终点不含解释。

## 最差五例（先定规则，后排序）

按主指标升序、ID升序取5页，包含相同模板的重复错误，不替换成更丰富的故事。以下差异是Codex对生成参考和原始预测的自动定位，具体视觉判断待本人核验。

### test_scan_03｜scan｜0.9011

[原页预览](previews/test_scan_03.png) · [原始Markdown](../runs/baseline-20261111T144702-4ebb49/test_scan_03/document.md) · [原始JSON](../runs/baseline-20261111T144702-4ebb49/test_scan_03/document.json) · [生成参考](../references/test_scan_03.json)

标记对顺序=0.0000；表格精确匹配=None；转换成功=True。

规范化差异定位（这是字符串对齐线索，不保证每段都能独立归因为OCR）：

```json
[
  {
    "operation": "delete",
    "expected": "第一",
    "predicted": ""
  },
  {
    "operation": "insert",
    "expected": "",
    "predicted": "第"
  },
  {
    "operation": "delete",
    "expected": "第二步",
    "predicted": ""
  },
  {
    "operation": "insert",
    "expected": "",
    "predicted": "第二步"
  }
]
```

### test_scan_07｜scan｜0.9011

[原页预览](previews/test_scan_07.png) · [原始Markdown](../runs/baseline-20261111T144702-4ebb49/test_scan_07/document.md) · [原始JSON](../runs/baseline-20261111T144702-4ebb49/test_scan_07/document.json) · [生成参考](../references/test_scan_07.json)

标记对顺序=0.0000；表格精确匹配=None；转换成功=True。

规范化差异定位（这是字符串对齐线索，不保证每段都能独立归因为OCR）：

```json
[
  {
    "operation": "delete",
    "expected": "第一",
    "predicted": ""
  },
  {
    "operation": "insert",
    "expected": "",
    "predicted": "第"
  },
  {
    "operation": "delete",
    "expected": "第二步",
    "predicted": ""
  },
  {
    "operation": "insert",
    "expected": "",
    "predicted": "第二步"
  }
]
```

### test_table_05｜table｜0.9149

[原页预览](previews/test_table_05.png) · [原始Markdown](../runs/baseline-20261111T144702-4ebb49/test_table_05/document.md) · [原始JSON](../runs/baseline-20261111T144702-4ebb49/test_table_05/document.json) · [生成参考](../references/test_table_05.json)

标记对顺序=—；表格精确匹配=False；转换成功=True。

规范化差异定位（这是字符串对齐线索，不保证每段都能独立归因为OCR）：

```json
[
  {
    "operation": "insert",
    "expected": "",
    "predicted": "上期本期"
  },
  {
    "operation": "delete",
    "expected": "上期本期",
    "predicted": ""
  }
]
```

### test_scan_01｜scan｜0.9231

[原页预览](previews/test_scan_01.png) · [原始Markdown](../runs/baseline-20261111T144702-4ebb49/test_scan_01/document.md) · [原始JSON](../runs/baseline-20261111T144702-4ebb49/test_scan_01/document.json) · [生成参考](../references/test_scan_01.json)

标记对顺序=0.3333；表格精确匹配=None；转换成功=True。

规范化差异定位（这是字符串对齐线索，不保证每段都能独立归因为OCR）：

```json
[
  {
    "operation": "insert",
    "expected": "",
    "predicted": "317"
  },
  {
    "operation": "delete",
    "expected": "317",
    "predicted": ""
  },
  {
    "operation": "delete",
    "expected": "一",
    "predicted": ""
  }
]
```

### test_scan_02｜scan｜0.9451

[原页预览](previews/test_scan_02.png) · [原始Markdown](../runs/baseline-20261111T144702-4ebb49/test_scan_02/document.md) · [原始JSON](../runs/baseline-20261111T144702-4ebb49/test_scan_02/document.json) · [生成参考](../references/test_scan_02.json)

标记对顺序=0.3333；表格精确匹配=None；转换成功=True。

规范化差异定位（这是字符串对齐线索，不保证每段都能独立归因为OCR）：

```json
[
  {
    "operation": "delete",
    "expected": "第一步",
    "predicted": ""
  },
  {
    "operation": "insert",
    "expected": "",
    "predicted": "第步"
  }
]
```

## 数据泄漏与负责任使用

test与dev、旧三页PDF无精确哈希重复；新test不训练、不调参，原始输出未手改。生成参考先于预测，排除按模型答案补标成功的做法。

**不能排除的偏差**：dev/test共享绘制模板，24页内容简单且相关；模型可能见过类似格式。只有哈希检查不能证明统计独立、没有预训练污染或现实代表性。新文档降低原页重复风险，但无法证明完全无污染。

新内容为CC0虚构教学材料，不含真实隐私；字体和模型许可分别继承已核对的第5/6周来源，见 [Dataset Card](../dataset-card.md)。没有私人文档上传或付费API调用。

## 限制与下一步

自动指标不评价所有结构：标点、空格、标题层级、公式、证据定位和真实长文档未覆盖。表格结构另测，不能把字符分高视为完全解析正确。原始模型失败和参考定义错误也需要分开。

自主探索选择“数据分布与切片”，结果见上表；没有用test改模型，也没有把扫描档位视为单变量因果实验。本人按 [集中核验清单](manual-review.md) 对照最差五页和一页最好结果，再说明一处自动分数遗漏的问题。

下周先另建训练/验证数据；本轮test保持冻结。如果参考需修正，保留v1并建立新版本，对全部方法统一重评。真实泛化需另建跨模板/真实授权文档测试集。
