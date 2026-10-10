# 实验过程与阶段记录

以下按实验过程合并历史说明；最终结论见 report.md。阶段待办保留其历史语境。


---

## reports/history.md

# 单图结果核对

运行：`single-20261010T112736-684304`。原始输出与配置见 `runs/` 同名目录，终端日志见 `evidence/logs/single-inference-after-fix.txt`。

- status: completed；模型加载约 132.55 秒，生成约 10.69 秒，总计约 143.77 秒。加载时间不能解释为纯推理时间。
- generated_tokens: 20；token_limit_reached: false。
- 原始答案：`A red square and a blue circle are positioned side by side on a white background.`
- 参考内容：左侧红色矩形，右侧蓝色圆形，白色背景；红色矩形宽约 100、高约 120，不是正方形。
- Codex 核对：颜色、圆形、白色背景与横向并排正确；square 不准确；未明确左右对应关系。建议评价 partial（形状错误、位置描述不完整），待用户人工确认。
- 结论范围：运行流程成功，单图回答并非完全正确；一张图不能支持总体准确率结论。
- 下一步：保持原图和模型，比较 A 直接提问与 B 证据约束。不要预先断言 B 会修复形状错误。


---

## reports/history.md

# 原图 Prompt 配对实验

运行目录：`runs/paired-20261010T115534-329139/`，运行状态 completed；原始终端日志见 `evidence/logs/prompt-pilot-console.txt`。

| 条件 | A | B |
| --- | --- | --- |
| Prompt | 原问题 | 原问题前增加可见证据与不确定性约束 |
| 图片哈希 | 8e6a61e851de66043c5fcddc96e77c4d599d1449593732addcd9ee8ec8232852 | 同 A |
| 生成 token | 20 | 16 |
| 达到上限 | 否 | 否 |
| 生成耗时（秒） | 18.24 | 6.75 |
| Codex 初步评价 | partial | partial |

A 原始答案：`A red square and a blue circle are positioned side by side on a white background.`

B 原始答案：` A red square and a blue circle are positioned side by side.`

两组都误称红色矩形为 square，并未明确左右对应关系。颜色、蓝色圆形与并排关系正确。B 更简短，但在此样例上未修复事实错误。人工评价表 review.csv 保留待填写，不将 Codex 初步评价写作用户已确认的人工结论。

模型 revision、图像、问题与生成参数相同；两组 input_tokens 为 127 / 159，差异来自 Prompt 长度。该配对用于检查 Prompt 约束，不足以判断所有 Prompt 策略无效，也不能据此判断错误具体发生在视觉编码还是生成阶段。

耗时属于单次运行，B 输出更短且固定后运行；不将时间差解释为约束 Prompt 必然加速。后续按原配置扩展到固定十张样例，共二十条结果，逐条核对后比较。


---

## reports/history.md

# 十张样例的首次完整对照（32 token）

证据目录：`runs/paired-20261010T143219-962222/`，status completed，20 条结果完整；总耗时约 206.35 秒，模型加载约 18.17 秒。

以下为 Codex 按预定 criteria 的初步核对，需用户结合图片确认；不将其写作用户已完成的人工评价。原始 review.csv 保留。

| 样例 | A 初步判断 | B 初步判断 | 要点 |
| --- | --- | --- | --- |
| shapes | 部分正确 | 部分正确 | 都误称 square，左右关系未明确 |
| count | 截断，未给数量 | 正确：7 | A 达到 32 token 上限 |
| position | 截断，未完成关系判断 | 正确：Above | A 达到上限 |
| invoice | 正确：AB-7093 | 正确：AB-7093 | 允许答案带字段名，不要求整句字符串相等 |
| dense_text | 正确：ZX-4108 | 正确：ZX-4108 | 行号匹配正确 |
| table | 截断，未给 Book 价格 | 正确：12 | A 达到上限 |
| chart | 截断，未给最终标签 | 正确：B | A 达到上限 |
| arithmetic | 截断，未给总价 | 错误：$7 | 正确总价 3×2+1×4=10；B 未达到上限 |
| missing_date | 已正确说明日期缺失，后续截断 | 正确：None | A 达到上限不等于核心答案错误；B 的 None 在此语境按无日期解读 |
| occluded | 未回答：Account code: | 错误/无依据：0 | A 仅 6 token，未截断；B 不应编造遮挡内容 |

A 六条达到 token 上限；其中 missing_date 已给出正确核心结论，其余五条未完成任务。B 无一达到上限。

按当前任务完成口径，初步计数 A：3 正确、1 部分正确、5 截断未答、1 未答；B：7 正确、1 部分正确、2 错误。仅为十个固定教学探针的描述性汇总，不是模型总体准确率，也不是用户已确认的评分。

## 能支持的结论

- 在 32 token 配置下，B 的简短回答使更多任务给出最终答案。
- B 不能保证事实正确：矩形、总价和遮挡内容仍有问题。
- 不能把 A 的未答全归因于 OCR、计数或推理能力；生成上限影响明显。
- 不将同一张 shapes 的 A/B 重复输出当成两个独立输入失败；目前尚未形成五个不同输入上的充分视觉失败证据。

## 下一步最小验证

在独立配置中仅将 max_new_tokens 从 32 增至 128，两组都运行全部十张图。原 Prompt、图像、模型 revision 与其他参数固定；结果放入新目录，原记录不覆盖。

先比较同一组同一图的 32/128，再比较 128 下的 A/B。检查 A 是否只是先解释再给答案，B 的 $7 和 0 是否仍然存在。128 仍可能不足，必须检查新结果的 token_limit_reached。


---

## reports/history.md

# 128 token 复验与 Prompt 比较

原始目录：`runs/paired-20261010T144254-776758/`，completed，20 条结果，总耗时约 238.88 秒。逐项检查证实与 32 token 轮的图片哈希、Prompt 相同，配置仅 max_new_tokens 从 32 改成 128。本轮无回答达到上限。

## Codex 初步核对（待用户确认）

| 样例 | A | B |
| --- | --- | --- |
| shapes | 部分正确：square 错误，缺少明确左右 | 同 A |
| count | 正确：7 | 正确：7 |
| position | 正确：Above | 正确：Above |
| invoice | 正确：AB-7093 | 正确：AB-7093 |
| dense_text | 正确：ZX-4108 | 正确：ZX-4108 |
| table | 正确：12 | 正确：12 |
| chart | 错误：C；图中 B 最高 | 正确：B |
| arithmetic | 正确：10 | 错误：7 |
| missing_date | 正确：日期缺失 | 正确：None，按缺失解读 |
| occluded | 未完成任务：仅重复 Account code: | 无依据回答：0 |

初步任务计数 A：7 正确、1 部分正确、1 错误、1 未答；B：7 正确、1 部分正确、2 错误。该计数仅描述十张教学图，不代表总体准确率。原始 review.csv 保留待填写，未冒充用户人工结论。

## 长度排查得到什么

A 的 count、position、table、arithmetic 补全后正确；chart 补全后反而暴露最终答案错误。missing_date 在 32 时已经说明缺失，本轮只是补全后文。

因此 32 token 轮的截断不能直接作为对应视觉任务能力不足的证据；完整解释也不保证正确。B 的答案保持原样，简短约束同时改变长度风格及实际答案，不能把观察到的差异全部归因于“依据证据”这几个词。

## 下一步

先由用户打开原图，核验 shapes、chart、arithmetic、occluded 的预定参考答案及评价条件，再确认人工评价。随后完善失败记录与例会解释；若扩展新的挑战输入，单独记录版本，不把相同图的 A/B 问题回答冒充两个独立输入证据。


---

## reports/history.md

# 算术图四组 Prompt 实验

原始目录：`runs/paired-20261010T150722-371103/`，status completed，约 52.35 秒。四组输入图片哈希相同，生成均未达到 128 token 上限。

## 实际完整 Prompt

### A：无额外约束
```text
Question: What is the total cost in USD?
```

### E：证据与不确定性约束
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What is the total cost in USD?
```

### S：简短要求
```text
Keep the answer brief. Question: What is the total cost in USD?
```

### B：两种约束
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What is the total cost in USD?
```

固定条件：Qwen/Qwen3.5-0.8B，revision 2fc06364715b967f1860aea9cf38778875588b17；CPU/float32、sdpa、4 线程、seed 42、do_sample=false、enable_thinking=false、max_new_tokens=128；参考答案 10，未传入模型；每组单独构造用户消息，无对话历史共享。

| 组 | 答案 | 新 token 数 | 评价 | 秒 |
| --- | --- | --- | --- | --- |
| A | 展示 3×2+1×4，最终 10 | 102 | 正确 | 26.08 |
| E | $7 | 5 | 错误 | 7.61 |
| S | $7 | 5 | 错误 | 6.60 |
| B | $7 | 5 | 错误 | 7.28 |

评价依据用户已确认的参考图；标签由 Codex 整理。

## 可支持与不可支持的结论

在此固定图及措辞下，A/E 和 A/S 分别显示单独加入证据约束或简短要求后答案从正确变为错误；E/B 与 S/B 则未显示额外答案变化。没有截断问题。

E 没有简短要求仍然输出短答案，所以不能将 B 的短回答或错误完全归于 Keep the answer brief；A 长解释也不是某个“详细模式”参数的结果。输出长度是观察结果，不是直接受控的相同量。

“7=3+4，因此忽略单价”仅是可能假设，当前短输出没有计算过程，不能据此确认。不要把解释文本视为内部计算过程的直接记录，也不要将单图表现扩大为证据约束或简短要求普遍降低正确性。

## 下一步

保持当前四组完整措辞及配置，扩展到已有十张教学图，共四十条输出。先核对达到上限情况，再按样例比较 A/E、A/S、E/B、S/B 的正确性及拒答行为。原算术图实验保留；全套记录放入新目录。


---

## reports/history.md

# 四组完整实验分析

证据目录：`runs/paired-20261010T152113-073899/`，completed，40 条输出，约 477.68 秒，无回答达到 128 token 上限。全部完整 Prompt 保存在各 JSON 的 prompt 字段与 `reports/prompts.md`，终端日志为 `evidence/logs/prompt-factors-full-console.txt`。

固定条件：Qwen/Qwen3.5-0.8B，revision 2fc06364715b967f1860aea9cf38778875588b17，CPU、float32、sdpa、4 线程、seed 42、do_sample=false、enable_thinking=false、max_new_tokens=128。四组独立消息，无共享对话历史，固定 A/E/S/B 顺序；时间不作严格性能 benchmark。

## 完整模板

所有 `{question}` 均由 configs/sample-manifest.json 中对应问题原文替换，不输入参考答案。

```text
A: Question: {question}
E: Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: {question}
S: Keep the answer brief. Question: {question}
B: Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: {question}
```

## Codex 初步任务答案评价

| 样例 | A | E | S | B |
| --- | --- | --- | --- | --- |
| shapes | 部分正确 | 部分正确 | 部分正确 | 部分正确 |
| count | 正确 7 | 最终数 7 正确，解释有错 | 错误 9 | 正确 7 |
| position | 正确 | 正确 | 正确 | 正确 |
| invoice | 正确 | 正确 | 正确 | 正确 |
| dense_text | 正确 | 正确 | 正确 | 正确 |
| table | 正确 | 正确 | 正确 | 正确 |
| chart | 正确 B | 错误 C | 正确 B | 正确 B |
| arithmetic | 正确 10 | 错误 7 | 错误 7 | 错误 7 |
| missing_date | 正确 | 正确 | 正确 | 正确 |
| occluded | 空回答 | 最终无法确定正确，解释存在措辞问题 | 编造 123456 | 无依据 0 |

按最终任务答案口径，A/E/S/B 的正确数为 8/7/6/7，分母均为十；不计部分正确为正确。这是固定教学样例上的计数，不是总体准确率。E 的 count 即使最终数正确，整段回答仍有错误，必须单独记录，不能称全部内容正确。

## 两个评价维度

1. 任务答案：最终数、字段或关系是否满足参考条件。
2. 解释忠实性：回答中的其他陈述是否也由可见证据支持，计算是否一致。

count/E 写中排 2，实际中排 3；并声称 3+2+1=7，实际这三个数相加为 6。最终数 7 碰巧正确不抵消解释错误。occluded/E 正确拒绝确认编号，但“box is empty”不如“contents are covered”准确：黑色遮挡不能证明底下没有内容。

## 可解释的观察与边界

- 证据约束 E 帮助遮挡图给出无法确定，却在图表和算术图上出错；它不是可靠性保证。
- 简短 S 在计数和算术图上出错，并在遮挡图编造编号；在其他多项任务上仍然正确。
- 加上证据约束后 S/B 在计数图由 9 变 7，在遮挡图则仍有无依据答案；因素影响随任务改变，不可简单相加。
- 所有组都误称红矩形为 square，空间关系不够明确；该措辞调整没有修复这个稳定错误。
- 历史无 Question: 前缀的 A/chart 答 C，本轮带前缀的 A/chart 答 B；不得把两者当作完全相同 Prompt 的重复。历史原始结果保留，提示措辞敏感。
- 非思考模式仍可以生成解释文字；这些文字不是内部思考过程的直接记录。无法从短答案证明模型内部算错原因。

## 下一步

用户对照 count.png 核对 3/3/1 排列及 E 的解释错误，之后确认评价维度与草稿。问题案例现覆盖 shapes、count、chart、arithmetic、occluded 五种不同输入，可整理五个代表性案例；无需为了凑数新增图片。

收尾阶段：核对人工评价、完成项目报告与原理说明；验证缓存复现入口；整理依赖和 Git 提交，再推送 GitHub。全新环境复现尚未完成，不能提前声明。


---

## reports/history.md

# Prompt 受控对照

研究问题：加入“只依据可见证据，无法确认时说明”的约束，是否改善固定样例上的回答？

## 配对设计

每张图片在 A、B 两组中完全相同；相同问题、模型 revision、CPU/float32、4 线程、seed 42、非思考模式、贪心生成与 32 新 token 上限。A 直接提问，B 增加证据约束。仅 Prompt 是实验变量。更长的 B Prompt 会增加输入 token，这是 Prompt 改动的一部分。

当前原图单图运行与 A 使用相同问题。新程序仍重新运行 A，使 A/B 都由同一程序、同一批次记录。程序一次加载模型，逐张运行，A 后 B；耗时是辅助记录，不将固定顺序下的耗时差异解释为严格速度结论。

## 从仓库根目录操作

```bash
source .venv/bin/activate
set -o pipefail
python -u week04/scripts/run_experiment.py --sample shapes 2>&1 | tee week04/evidence/logs/prompt-pilot-console.txt
```

先只对原图运行 A/B 两条回答，核对新 runs/paired-* 中的 `shapes-A.json`、`shapes-B.json` 和 `review.csv`。完成理解和核验后，再运行全套：

```bash
python -u week04/scripts/run_experiment.py 2>&1 | tee week04/evidence/logs/paired-full-console.txt
```

程序使用本地缓存，`--prepare-only` 只检查输入格式，不运行模型。完整样例可由 `python week04/scripts/prepare_samples.py` 重建；Ubuntu 需要系统 DejaVuSans 字体。图像版权声明见 samples/README.md，字体许可独立，不将字体文件上传仓库。

## 人工评价

按 configs/sample-manifest.json 的 criteria 核验，可在 review.csv 填入 verdict（correct / partial / incorrect / undetermined）、error_category（OCR / spatial / counting / reasoning / hallucination，可组合）和 notes。参考答案保存在记录中用于评价，但不会传给模型。

不要直接用英文字符串全等比较：同义表达可以正确，流畅文字也可以错误。先检查 token_limit_reached；达到上限时人工核对是否截断，不自动当作视觉错误。若需要增大上限，应另建配置并重新运行 A/B，将其作为单独实验，不混入当前结果。

本集合为自制教学探针，没有代表性数据抽样。可以描述配对样例上的变化，不能据此给出模型整体准确率。后续至少五个失败案例必须来自实际回答；环境加载错误不计入视觉失败。

## 官方依据

- [Multimodal chat templates](https://huggingface.co/docs/transformers/main/chat_templating_multimodal)：图片与文字同时放入 content，Processor 生成模型输入。
- [Generation](https://huggingface.co/docs/transformers/main/main_classes/text_generation)：do_sample 与 max_new_tokens 的生成控制。
- [Qwen3.5](https://huggingface.co/docs/transformers/model_doc/qwen3_5)：多模态模型与处理器、缺少优化内核时的 PyTorch 回退。

当前安装 Transformers 5.17.0；链接中的 main 文档会更新，接口使用已通过当前安装版本的本地检查。


---

## reports/history.md

# 拆分证据约束与简短要求

原 B 同时包含两项要求：可见证据/不确定性约束，以及 Keep the answer brief。原 A 没要求详细回答；较长解释是此次默认输出，不能声称 A 被指定为详细模式，也不能声称简短要求必然导致算错。

新实验保持 128 token 预算，固定所有样例、模型与其他参数，使用四个条件：

| 组 | 证据约束 | 简短要求 |
| --- | --- | --- |
| A | 无 | 无 |
| E | 有 | 无 |
| S | 无 | 有 |
| B | 有 | 有 |

所有组统一 `Question:` 标签，包括新 A，避免标签本身混入因素。新 A 因此与历史 A 存在格式差异，四组属于独立新实验，应以本轮 A 为基准。

固定简短条件时比较 A/E 或 S/B，观察证据约束影响；固定证据条件时比较 A/S 或 E/B，观察简短要求影响。比较问题答案与实际 token 数，128 是上限，不要求输出满 128。

先运行算术图四组，其他样例随后按需要扩展：

```bash
python -u week04/scripts/run_experiment.py --config configs/experiment-config-factors.json --sample arithmetic 2>&1 | tee week04/evidence/logs/prompt-factors-arithmetic-console.txt
```

本轮只回答“此前 B 的错误可能与哪个 Prompt 部分相关”。即使 E 正确、S 错误，也只说明这个输入上的关联，不证明内部推理机制或普遍规律。解释文字是模型生成内容，不是内部思考的直接观测。结果均保存到独立 paired 目录。

官方背景：[生成参数](https://huggingface.co/docs/transformers/main/main_classes/text_generation)说明 max_new_tokens 是输出上限；[聊天模板](https://huggingface.co/docs/transformers/main/chat_templating_multimodal)说明文本指令与图片如何形成模型输入。


---

## reports/history.md

# 失败分析草稿（Codex 核对，待用户人工确认）

依据 128 token 轮，每项均未达到上限。按四张输入聚合，保留六条问题回答：shapes A/B、chart A、arithmetic B、occluded A/B。相同输入的两组不是独立样例。

| 输入与输出证据 | 观察 | 暂定分类 | 当前不能断言的部分 |
| --- | --- | --- | --- |
| shapes-A.json / shapes-B.json | 红矩形误称 square，未明确左右关系 | 形状感知错误、空间描述遗漏 | 不能定位到视觉编码或语言生成内部 |
| chart-A.json | 声称 C 最高；图中 B 最高，B 组正确 | 视觉比较/推理 | 不能仅凭答案确定错误由读图还是比较过程引起 |
| arithmetic-B.json | 答 $7，图中应 3×2+1×4=10，A 组正确 | 推理或信息读取 | 未展示中间过程，不能断言一定把 3 和 4 相加 |
| occluded-A.json | 仅输出字段名，不说明无法确定 | 未完成回答 | 不属于长度截断，也不等同编造数字 |
| occluded-B.json | 答 0，无可见数字支持 | 幻觉/无依据回答 | 不读取生成脚本中遮挡前文字作为可见参考 |

证据均在 `runs/paired-20261010T144254-776758/`。分类针对可观察输出，不声称已证明内部机制。

需要用户核验：红色图形不是正方形；柱 B 最高；总价 10；遮挡图不能确认完整编号。后续在已确认输入与评价口径上记录案例，而非为了数量把环境错误或被截断的回答归作视觉错误。
