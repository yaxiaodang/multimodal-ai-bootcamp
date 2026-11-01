# 环境与命令说明

本周使用 Ubuntu 虚拟机中的 Python 3.10 独立环境 `.venv-week06`。VS Code 通过 Remote SSH 连接后，终端命令在 Ubuntu 中执行。用环境内解释器的完整路径，可避免误用系统 Python 3.14 或其他周的环境。

## 基础工作由 Codex 完成

以下命令用于说明与未来复现；当前学习者无需重复安装。安装和检查的实际完成状态以 evidence/ 中记录及 README 为准。

```bash
python3.10 -m venv .venv-week06
```

作用：创建独立虚拟环境。本机由已有 Python 3.10.12 执行等效操作，不修改系统 Python。

```bash
.venv-week06/bin/python -m pip install -r week06/requirements.txt
```

作用：在第六周环境安装 Docling、RapidOCR 与 CPU 版 PyTorch 等依赖。CPU 软件源配置在依赖文件中；依赖解析后的完整版本保存到 requirements-lock.txt。安装阶段如遇直接访问 PyPI 的 TLS 错误，Codex 使用现有 HTTPS 代理，仅为安装子进程清空 NO_PROXY/no_proxy，不改全局网络配置，不记录代理凭据。

已完成版本固定后，新环境可将上述命令的依赖文件换为 `week06/requirements-lock.txt`，作用是安装本轮全部解析出的依赖版本；系统与 Python 仍须匹配。

```bash
.venv-week06/bin/python week06/scripts/prepare_models.py
```

作用：下载本轮版面、准确表格和中文 OCR 模型到 `.cache-week06/artifacts/`，记录来源、许可与 SHA-256；不解析 PDF。模型卡和 revision 见 evidence/model-sources.json，OCR 源地址见 evidence/ocr-sources.json。权重只留本机，忽略目录不提交 GitHub。

```bash
.venv-week06/bin/python week06/scripts/verify_setup.py
```

作用：校验模型文件哈希并初始化 CPU 解析器，验证本地权重可离线加载；不调用文档转换，不生成学习实验结果。

```bash
.venv-week06/bin/python -m pip check
```

作用：检查已安装 Python 包之间的依赖是否兼容；不下载模型、不解析 PDF。

```bash
.venv-week06/bin/python week06/scripts/run_pipeline.py --prepare-only
```

作用：校验依赖版本、三份输入的哈希、参考文件及解析选项；不初始化解析器，不下载权重，不创建实验目录。准备通过不等于实验成功。

```bash
.venv-week06/bin/python week06/scripts/test_pipeline.py
```

作用：执行五项工程检查，验证导出格式与损坏 JSON 拒绝、哈希不符会被拒绝、准备检查不创建运行目录、单份失败或超时会保留日志并继续。合成文档对象与故障注入只在临时目录中使用，不执行真实 PDF 解析，也不作为学习实验结果。

## 本人亲自执行的学习实验

进入实验阶段后，在仓库根目录执行：

```bash
.venv-week06/bin/python week06/scripts/run_pipeline.py
```

作用：用默认 baseline.json 顺序解析三份固定 PDF，开启 OCR 与表格结构解析，使用 CPU、2 个线程，每份最多 600 秒。每轮新建 runs/baseline-时间-标识/；每份文档分别保存 document.md、document.json、stdout.log、stderr.log、转换状态和机械检查结果。整轮还保留配置、参考和源码快照、运行元数据与空白人工 review.csv。

程序结束码：0 表示转换及文件/格式检查通过；1 表示至少一份处理或机械检查失败；2 表示配置、输入或环境准备失败；130 表示用户中断。单文档超时在其记录中标为 124。以上均不代表内容或结构已被本人判断正确。

无需先激活环境。若终端位置不同，可先运行：

```bash
cd /home/yaxiaodang/multimodal-ai-bootcamp
```

作用：将当前终端切换到本仓库，让后续相对路径从仓库根目录解析。

## 配置的含义

- OCR 处理扫描图像中的文字；不是文档问答。本轮使用 RapidOCR 的中文兼容识别设置，实际模型和后端在准备时核实记录。
- `force_full_page_ocr=false`：不强制将每张数字页全部重新 OCR，按解析器选出的图像区域处理。
- 表格结构解析开启，模式为 accurate，单元格匹配开启；这些是待验证的设置，不保证合并范围正确。
- 公式增强关闭；Q10 的公式作为额外观察，不能把未启用专门增强等同于已完成公式任务。
- 每份文档由独立子进程处理，隔离失败并便于超时退出；耗时包含模型加载，不是纯推理时间，也不能代表本人学习时长。
- 原始导出不人工修补；本人在对话中反馈观察，由 Codex 整理核对表并保留证据定位。
