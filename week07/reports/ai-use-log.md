# AI 使用与核验记录

工具：Codex；本轮未独立记录客户端版本。不声称用户已亲自执行或理解代码。

| 阶段 | Codex完成/建议 | 采用的判断与验证 | 本人状态 |
| --- | --- | --- | --- |
| 任务核对 | 阅读第7周路线、记录模板与Dataset Card官方说明 | 把交付映射为24页固定test、3页dev、card、manifest、冻结、baseline、切片、最差5例 | 学习反馈待补 |
| 数据设计 | 新制虚构中文PDF，生成规格给参考 | 未复用上周已看过的3页当测试集；保留模板共享偏差；27页检查为单页、scan无字体层；Codex查看代表三页 | 原页与参考视觉核验待补 |
| 实验与指标 | 直接复用Week06 Pipeline；冻结指标后运行 | 不因test低分改参数；正文序列主分之外加顺序、表格结构；手算/篡改/结构测试通过 | 无本人评分输入 |
| 报告 | 自动生成全样例指标、切片、最差五例与差异定位 | 失败样例不得从分母删除；按预定排序保留五例；结论限于当前数据 | 五例与最好一例待本人集中观察 |
| 归档 | 更新说明与模板学习记录，提交本周内容 | 保留既有用户未提交改动；报告AI运行不写为用户亲自完成 | 实际时长、自评及演练待补 |

设计中主动限制的建议：不把已有三份开发页复制扩增成可信新测试集；不使用测试集做Prompt选择；不凭字符都出现就认定合并表格正确；不将自动运行、Codex文档检查或生成参考冒充本人学习/人工标注。它们是Codex的设计取舍，不编造为用户曾经提出或拒绝的建议。

当前人工核验仅指用户后续亲自提供的反馈，尚未发生。Codex完成的图片检查、源码阅读、工程测试和官方资料核对单列披露。

本周不修改Week06解析实现、不复制模型文件、不新增网络上传逻辑。GitHub仅保存用户授权的本仓库实验与虚构材料。输入和参考使用相对路径，模型缓存继续留在忽略目录；无API密钥进入新增文件。

官方依据：[课程路线](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/)、[记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)、[Dataset Cards](https://huggingface.co/docs/hub/datasets-cards)、[OmniDocBench](https://github.com/opendatalab/OmniDocBench)。只是参考数据与评测设计，没有运行OmniDocBench官方工具。
