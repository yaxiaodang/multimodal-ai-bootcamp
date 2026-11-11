# 验证记录

- 冻结Week07/08数据及模型/adapter哈希通过；A/B唯一算法差异learning_rate，PDF唯一算法差异do_ocr。
- 原始输出producer SHA256重新认证，三个文本模型预测与reserved-test逐条ID、输入、答案对齐。
- 手算字符距离与JSON严格字段边界测试通过（2个测试方法，包含多种边界）。
- 从原始结果重算5组实验，manifest认证323个文件；42个错误case，涉及16个唯一PDF与12个唯一文本样例，自动标签待本人确认。
- 首次系统Python核验因sum(float)实现与Python3.10的末位舍入差异而失败；比较使用1e-12容差后通过，原始预测、指标定义与报告实测数字不变。该容差只用于核验。
- 24页无OCR子任务整体exit=1：8个扫描页机械质量失败，保留所有负面输出与日志；文本调度exit=0。详细命令/退出码见execution.json。
- Markdown本地主链接检查通过；图表已经查看；git diff --check通过。
- 未做：全新VM安装复现、本人人工复核、云端W&B同步/Report、计时受控复测、多seed训练。
