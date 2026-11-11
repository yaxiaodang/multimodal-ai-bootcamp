# 证据索引

| 文件 | 作用 |
| --- | --- |
| manifest.json | SHA256固定本周静态交付、结果及上游manifest/全部被引用文件；不对动态回执自哈希 |
| release-files.json | 发布候选清单及单文件10MiB上限；包只取Git已提交文件 |
| execution.json | 最近一次运行的环境、命令、状态与耗时；重算会更新 |
| week10-audit.log、week11-audit.log | 独立核验的原始输出，返回非0时入口停止 |
| release-audit.json | 文件模式/大小检查，不输出可能匹配的凭据内容 |
| reproduction-check.json | 当前VM、隔离clone及压缩包解压重算的结果，区分AI与同学 |
| validation.json | 正向核验及篡改/缺失输入等负向检查 |
| ai-usage.md | AI范围、自动与人工核验的区分 |

动态回执、本文件列出的个人填写文件不纳入冻结SHA；旧周原始输入、预测、配置与adapter仍受各自manifest保护。若本人要纠正冻结报告，不应只改SHA掩盖变化，应另存版本、说明原因并重新验证。历史未提交笔记与PDF内容不并入本周发布提交。
