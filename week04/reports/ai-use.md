# AI 使用与人工核验

工具：Codex；具体模型版本未单独记录。日期：2026-10-10。

- AI 辅助：路线核对、资源与模型选择建议、目录整理、程序及样例生成、依赖修复、结果核对、评价与报告。
- 用户执行：调整 Ubuntu 资源，在 VS Code Remote SSH 终端执行模型访问、单图及各轮对照推理；核对 shapes、chart、arithmetic、occluded、count 的参考事实，确认双维度评价规则。
- 证据核验：保留完整 Prompt、配置、revision、图片哈希、原始回答和终端日志；Codex 检查已保存证据的一致性，用户复现推理尚待执行。
- 修改与取舍：缺少 torchvision 通过安装兼容 CPU 包解决；32 token 截断通过独立 128 配置排查；原组合 Prompt 未区分两因素，另建 A/E/S/B；此前说明漏掉 Keep the answer brief，已更正并在终端打印完整 Prompt。
- 评价范围：标签由 Codex 根据原始输入/输出与用户确认的规则整理，不称用户已逐条签署四十条标签；评价表保留 user_review/user_notes。
- 限制：未证明模型内部错误原因；没做正式 benchmark、跨机器或全新环境复现；本周实际总学习耗时未完整记录。
