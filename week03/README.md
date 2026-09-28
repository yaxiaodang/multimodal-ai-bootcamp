# Week 03：AI 辅助编程与人工验证

## 本周目标

以 Week 1 的图片信息工具为对象，练习“定义任务 → 获取 AI 建议 → 人工审查 → 运行验证 → 记录取舍”的开发流程。

本周没有重新开发一个图片工具，而是在原有工具上明确支持格式：正常处理实际格式为 PNG 或 JPEG 的图片；对于能够识别但不支持的真实图片格式，例如 BMP，给出清晰错误。

## 开发与运行环境

- 开发方式：Windows VS Code 通过 Remote SSH 连接 Ubuntu 虚拟机。
- Python：3.10.12。
- Pillow：11.3.0。
- pytest：8.4.1。
- 运行设备：CPU；本周任务不需要 GPU。
- Week 3 分支：`feat/week03-ai-validation`。

以上版本是本次实际运行时的记录，不表示其他环境必须显示完全相同的测试耗时。

## 本周修改了什么

- `week01/src/image_info.py`：使用 Pillow 识别出的实际图片格式，只接受 PNG 和 JPEG；对其他已识别格式给出“不支持”的错误。
- `week01/tests/test_image_info.py`：保留原有三个测试，并补充 JPEG、1×1 PNG、真实 BMP、BMP 命令行行为，以及文件扩展名与实际内容不一致的场景。
- 成功时的返回字段和命令行四行输出保持原有形式。
- 本周没有修改 Week 2 的模型推理代码，也没有新增 Python 依赖。

工具仍位于 `week01/`，因为 Week 3 改进的是 Week 1 的原工具；`week03/` 用于保存本周的任务、AI 协作、审查和测试证据。

## 文件说明

| 文件 | 作用 |
|---|---|
| `task-card.md` | 记录目标、约束、边界与验收标准 |
| `ai-use-log.md` | 记录 Copilot 的关键建议、人工判断、测试与修正 |
| `code-review.md` | 审查正确性、边界、安全、依赖、许可及剩余限制 |
| `test-before-fix.txt` | 修改实现前的测试输出：7 项测试中 2 项失败、5 项通过 |
| `test-after-fix.txt` | 修改实现后的完整测试输出：9 项测试全部通过 |
| `../week01/src/image_info.py` | 实际修改的图片信息工具 |
| `../week01/tests/test_image_info.py` | 本周扩充的自动化测试 |

## 如何运行

在通过 Remote SSH 连接 Ubuntu 的 VS Code 终端中，从仓库根目录激活已有的虚拟环境：

```bash
cd ~/multimodal-ai-bootcamp
source .venv/bin/activate
cd week01
```

查看正常样例：

```bash
python src/image_info.py samples/demo.png
```

本次运行的输出为：

```text
file: samples/demo.png
width: 640
height: 480
format: PNG
```

查看工具帮助：

```bash
python src/image_info.py --help
```

运行全部测试：

```bash
python -m pytest -q
```

本次验证结果为：

```text
9 passed in 0.23s
```

测试图片由测试代码在临时目录中生成，因此不需要手动准备 JPEG 或 BMP 图片。具体测试名称可通过以下命令查看：

```bash
python -m pytest --collect-only -q
```

本次共收集到九项测试。重跑时，临时目录名称和测试耗时可能变化。

如果是在新环境复现 Week 3 工具，需要先按照仓库根目录的依赖文件安装 Pillow 和 pytest；Week 2 的模型推理环境另有依赖记录，本周图片工具不需要加载 Week 2 的模型。

## 验证过程与结果

本周保留了修改前后的两组证据：

| 阶段 | 实际运行情况 | 说明 |
|---|---|---|
| 原有基线 | 3 项原有测试通过 | 确认原工具可运行 |
| 补充首批测试、修改实现之前 | 2 failed，5 passed | 真实 BMP 被错误接受；CLI 对 BMP 返回成功 |
| 修改实现并补充扩展名边界测试之后 | 9 passed | PNG/JPEG、BMP 错误路径及扩展名边界均通过 |

改动前运行的是七项测试；后补的两项扩展名边界测试没有被写成“改动前已运行”。

另外手动运行了现有 PNG 样例和 `--help`：样例仍输出原有四行信息，帮助信息正常显示。错误 BMP 的命令行行为由自动化测试验证。

## AI 使用披露与人工责任

本周在 VS Code 中使用 GitHub Copilot 进行需求审查、测试场景设计和最小实现补丁建议；具体 Copilot 模型未在本次记录中显示。ChatGPT 用于步骤规划、审查建议、补充边界测试场景和文档草稿。

AI 提出的内容没有直接视为正确结论。我根据 Task Card 审查改动范围，补充了 Copilot 首批测试未覆盖的两个场景：实际 BMP 内容使用 `.png` 文件名，以及文本内容使用 `.png` 文件名；随后在 Ubuntu 虚拟机中运行测试、查看实现 diff，并记录真实结果。

三轮关键协作及人工判断见 `ai-use-log.md`。实现审查与限制见 `code-review.md`。最终代码和结论的核对责任由我承担。

## 当前限制

- 只处理单张本地图片，不支持目录批量处理。
- 只接受实际格式为 PNG 或 JPEG 的图片。
- 不支持 PDF、OCR 或图像内容理解。
- 当前没有通过完整解码全部像素来验证每一种损坏或截断图片。
- 当前没有为任意不可信大图片设置文件大小或解码资源上限。
- 测试覆盖了本次任务卡指定的正常与异常场景，不代表对所有输入都完成了穷尽验证。

## 本周完成标准

- [x] 编写包含约束与验收标准的 Task Card。
- [x] 记录三轮关键 AI 协作和人工判断。
- [x] 完成至少三个正常场景、两个异常场景的测试。
- [x] 保存修改实现前后的实际测试输出。
- [x] 审查实现 diff，并运行完整测试。
- [x] 检查原有 PNG 命令行输出和 `--help`。
- [x] 记录 AI 使用范围、人工补充及当前限制。
- [x] 检查最终测试文件 diff 和 Git 工作区。
- [x] 完成 Week 3 的 Git 提交及后续 PR 流程。