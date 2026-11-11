# Week11 复现计划（首次实验前固定）

登记日期：2026-11-11（北京时间）。这是仓库内的事前计划，不是第三方预注册平台；制定时已知Week08/09的r8在同一validation达到12/12，故不是盲法发现性研究。计划与配置先提交Git，再启动Week11新训练；不重复利用Week10已消费的reserved-test证明泛化。

## 问题与范围

选LoRA论文arXiv:2106.09685v2，针对§4.1的低秩更新机制和§7.2的rank研究思路。验证一个缩小主张：在现有合成英文账单开发集上，仅训练q_proj/v_proj低秩矩阵、冻结全部基座参数，r4能否改善字段抽取；并验证训练后的低秩支路可以合并回基座且保留输出。

这是**机制复现与本地迁移验证**，不复现论文benchmark分数，不证明LoRA胜过全参数微调。复用Week08训练代码，Week11重新执行r4和r8，不把旧实验当新运行。

## 固定协议

- 模型：HuggingFaceTB/SmolLM2-135M，revision 93efa2f097d58c2a74874c7e644dbc9b0cee75a2；CPU FP32，PEFT0.19.0。
- 数据：Week08 v1，96 train / 12 validation；固定freeze.json和Prompt；reserved-test只验哈希，不加载作预测或选参。Week07 PDF不参与。
- 两run仅r=4/8不同（name为身份标签）；alpha=16不变，因而alpha/r=4/2也随r变化。只能解释为该参数化下rank设置的整体效果，不能隔离纯容量与缩放效应。
- seed42，q_proj/v_proj，dropout0，AdamW lr0.001，batch2×累积2，60步，固定最终步数，不挑最好checkpoint；greedy最多32新token。
- baseline在每run训练前保存；主指标严格JSON字典与参考完全相等的比例；辅助指标JSON合法率、total/currency正确率、参考答案NLL。NLL用参考答案teacher forcing，不能代替自由生成准确率。

## 运行前成功标准

1. r4训练后validation strict exact >= 0.75，且相对同run baseline提升 >= 0.50；若未达到，保留结果并报告本地不支持，不加步数或改阈值。
2. 两run所有可训练参数名均为lora_A/B，数量占“基座+adapter”参数 < 1%；全部非LoRA参数训练前后SHA256完全相同；保存后重加载预测一致。
3. r4/r8可训练参数数量恰好1:2。效果是否同分属于探索，不预设r4优于r8，不要求r4追平r8才算主任务完成。
4. 对两run、全部12个validation Prompt的全位置logits，合并前后torch.allclose(atol=1e-4, rtol=1e-4)，greedy生成文本逐条一致；合并后无lora_参数。另对全部60个注入层核对delta=(alpha/r)BA与PEFT实现一致。
5. 从零初始化的新adapter在12个Prompt上不改变base logits（同上容差），所有B为0、A非零。PEFT默认A为Kaiming uniform，论文A为Gaussian：明确记录这一差异，不把它写成相同初始化。

## 预算与停止条件

- 仅使用已缓存的公开模型和现有CPU虚拟环境；GPU0、付费云0，不安装新包。
- 每run训练循环900秒上限，子进程总上限1200秒；机制核验每run300秒；顺序执行避免内存竞争。任一异常、哈希不符、非有限loss、超预算即停止，保留日志及失败状态，不静默重跑。
- 参考历史约每run5分钟；整套预算50分钟，禁止为提高分数追加配置/seed。数据量、线程、steps均不变。
- 原始配置、源码快照、环境、日志、adapter、预测、每步loss及核验JSON入库。base缓存与整份合并模型不上传；manifest列SHA256。

## 推论边界与后续

同模板12条validation、单seed，有模板/币种相关性，且本次计划参考了历史结果。没有独立最终测试、视觉输入、全参数训练对照、重复测速或跨机器复现。参数量减少不等于总内存同比减少，合并数值一致不等于实测零延迟。论文事实/作者解释/本地观察/个人猜想分开陈述。

一次自主探索：rank4与8在固定alpha下的参数量/本地指标对照。若继续研究需另建开发数据打破模板与币种关联，之后再申请全新未消费的最终测试；不更改本轮数据。
